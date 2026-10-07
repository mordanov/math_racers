# Sprint 3 — Avatar Flow + Job Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Avatar Gallery page, the 5-step Avatar Creator wizard, and backend job-retry backoff so failed AI generation jobs retry automatically with exponential delays instead of silently staying stuck.

**Architecture:** Backend: a new Alembic migration adds `retrying` and `permanent_failure` to the `GenerationJob.status` check constraint; `generation_service._run_pipeline` sets `retrying` between attempts and sleeps the backoff interval before each retry. Frontend: `AvatarGalleryPage` fetches the avatar list and polls every 3 s while any avatar is `pending`; `AvatarCreatorPage` is a 5-step wizard (species → colour → style → clothing → reveal) that calls `POST /api/v1/avatars` and polls the returned job until it reaches `complete` or `permanent_failure`.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy / Alembic / asyncio, React 18 / TypeScript / Vitest / Testing Library, pytest-asyncio for backend async tests.

**Spec:** `docs/superpowers/specs/2026-10-05-v1-execution-order-design.md` (Sprint 3 section), `docs/content/feature-avatar-creation.md`, `docs/content/spec-avatar-generation.md`, `docs/ui/spec-ui-implementation.md`.

## Global Constraints

- All new Python functions must have `-> None` or explicit return type annotations (mypy `no-untyped-def`).
- All backend files formatted with Black; linting passes Ruff.
- All frontend files formatted with Prettier (`npx prettier --write`).
- Accessibility: every interactive element keyboard-reachable; focus ring 2px solid `#60A5FA`; text contrast ≥ 4.5:1; `prefers-reduced-motion` disables non-essential animations.
- Children must never see technical error text — use child-friendly messages as defined in `docs/ui/screens.md §Child-Facing Error Messages`.
- All test functions in Python test files require `-> None` return annotation.
- No new npm packages — use existing dependencies (React, react-router-dom, @testing-library/react, vitest, msw).
- Image asset paths: static images live in `assets/` at the repo root, referenced from frontend as `../../assets/...` relative to `src/pages/`, or import them at the top of the file.

## Review Focus

1. **`retrying` job abandoned after worker crash** — if the worker process dies while sleeping the backoff, the job stays in `retrying` state forever and the gallery shows a permanent spinner. Expected: gallery eventually shows an error state. `Task 2` adds a test verifying `run_generation_job` treats `retrying` as a processable state so it can be re-dispatched.
2. **Polling never stops for `permanent_failure` status** — `useAvatarGallery` polls every 3 s while any avatar is `pending`; if it doesn't stop when the avatar reaches `permanent_failure` (which has `status: 'failed'` on the avatar), it runs forever. Expected: polling stops when no avatar has `status === 'pending'`. `Task 4` adds a test verifying the interval is cleared when the re-fetched list contains no pending avatars.
3. **Wizard back-navigation loses selections** — user picks species in step 1, advances to step 2, presses Back: their species choice should survive. Expected: state is held in the parent wizard component and re-rendered when step changes. `Task 5` adds a test: pick species → advance → go back → species selection is still checked.
4. **Empty gallery with an in-progress job** — when no avatars are `published` but one is `pending`, the gallery should show a skeleton/generating card, NOT the empty-state illustration with "Create Your First Avatar". Expected: empty state is shown only when `avatars.length === 0`. `Task 4` adds a test verifying the gallery renders a "Generating…" card when the only avatar has `status: 'pending'`.
5. **No polling started when all avatars are already `published`** — opening the gallery when every avatar is `published` should never start the polling interval. Expected: `setInterval` is never called when there are no pending avatars. `Task 4` adds a test verifying no interval is set when the initial list contains only published avatars.

---

### Task 1: Backend — Job retry states: migration + model + frontend type

**Files:**
- Modify: `backend/app/avatars/models.py` — update `ck_generation_jobs_status` check constraint
- Create: `backend/alembic/versions/0011_job_retry_states.py` — migration to drop/recreate the constraint
- Modify: `frontend/src/engine/avatar/types.ts` — add `'retrying' | 'permanent_failure'` to `JobStatus`
- Create: `backend/tests/unit/avatars/test_job_retry_model.py` — verify constraint contains new states

**Interfaces:**
- Produces: `JobStatus` type in `frontend/src/engine/avatar/types.ts` now includes `'retrying'` and `'permanent_failure'` — Tasks 4 and 5 reference these values when checking job progress.

- [ ] **Step 1: Write the failing test**

  Create `backend/tests/unit/avatars/test_job_retry_model.py`:

  ```python
  """Unit tests — GenerationJob model includes retry states."""

  from __future__ import annotations

  import pytest

  from app.avatars.models import GenerationJob


  @pytest.mark.unit
  def test_generation_job_status_constraint_includes_retrying() -> None:
      constraint = next(
          c
          for c in GenerationJob.__table_args__
          if hasattr(c, "name") and c.name == "ck_generation_jobs_status"
      )
      assert "'retrying'" in constraint.sqltext.text


  @pytest.mark.unit
  def test_generation_job_status_constraint_includes_permanent_failure() -> None:
      constraint = next(
          c
          for c in GenerationJob.__table_args__
          if hasattr(c, "name") and c.name == "ck_generation_jobs_status"
      )
      assert "'permanent_failure'" in constraint.sqltext.text
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_job_retry_model.py -v
  ```
  Expected: FAIL — `AssertionError` because `'retrying'` is not in the current constraint text.

- [ ] **Step 3: Update `backend/app/avatars/models.py`**

  Find the `CheckConstraint` for `ck_generation_jobs_status` in the `GenerationJob.__table_args__`:

  Replace:
  ```python
  CheckConstraint(
      "status IN ('queued','llm_running','prompt_building','generating','validating',"
      "'storing','complete','failed')",
      name="ck_generation_jobs_status",
  ),
  ```
  With:
  ```python
  CheckConstraint(
      "status IN ('queued','llm_running','prompt_building','generating','validating',"
      "'storing','complete','failed','retrying','permanent_failure')",
      name="ck_generation_jobs_status",
  ),
  ```

- [ ] **Step 4: Run test to verify it passes**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_job_retry_model.py -v
  ```
  Expected: PASS 2/2.

- [ ] **Step 5: Create the Alembic migration**

  Create `backend/alembic/versions/0011_job_retry_states.py`:

  ```python
  """add retrying and permanent_failure states to generation_jobs

  Revision ID: 0011
  Revises: 0010
  Create Date: 2026-10-06
  """

  from __future__ import annotations

  from alembic import op

  revision: str = "0011"
  down_revision: str | None = "0010"
  branch_labels = None
  depends_on = None


  def upgrade() -> None:
      op.drop_constraint("ck_generation_jobs_status", "generation_jobs", type_="check")
      op.create_check_constraint(
          "ck_generation_jobs_status",
          "generation_jobs",
          "status IN ('queued','llm_running','prompt_building','generating','validating',"
          "'storing','complete','failed','retrying','permanent_failure')",
      )


  def downgrade() -> None:
      op.drop_constraint("ck_generation_jobs_status", "generation_jobs", type_="check")
      op.create_check_constraint(
          "ck_generation_jobs_status",
          "generation_jobs",
          "status IN ('queued','llm_running','prompt_building','generating','validating',"
          "'storing','complete','failed')",
      )
  ```

- [ ] **Step 6: Update `frontend/src/engine/avatar/types.ts`**

  Replace:
  ```typescript
  export type JobStatus =
    | 'queued'
    | 'llm_running'
    | 'prompt_building'
    | 'generating'
    | 'validating'
    | 'storing'
    | 'complete'
    | 'failed';
  ```
  With:
  ```typescript
  export type JobStatus =
    | 'queued'
    | 'llm_running'
    | 'prompt_building'
    | 'generating'
    | 'validating'
    | 'storing'
    | 'complete'
    | 'failed'
    | 'retrying'
    | 'permanent_failure';
  ```

- [ ] **Step 7: Run full backend unit suite to check for regressions**

  ```bash
  cd backend && python -m pytest tests/unit/ -v
  ```
  Expected: all existing unit tests PASS.

- [ ] **Step 8: Run frontend type-check to verify type change compiles**

  ```bash
  cd frontend && npx tsc --noEmit
  ```
  Expected: no errors.

- [ ] **Step 9: Commit**

  ```bash
  git add backend/app/avatars/models.py \
          backend/alembic/versions/0011_job_retry_states.py \
          backend/tests/unit/avatars/test_job_retry_model.py \
          frontend/src/engine/avatar/types.ts
  git commit -m "feat(avatars): add retrying/permanent_failure job states and migration"
  ```

---

### Task 2: Backend — Retry backoff logic in `generation_service.py`

**Files:**
- Modify: `backend/app/avatars/generation_service.py` — add `_backoff_seconds`, update `_run_pipeline`, update `run_generation_job`
- Create: `backend/tests/unit/avatars/test_generation_retry.py`

**Interfaces:**
- Consumes: `GenerationJob.status` now allows `'retrying'` and `'permanent_failure'` (Task 1).
- Produces: exported `_backoff_seconds(attempt_just_failed: int) -> int` for tests; `run_generation_job` now also processes jobs in `retrying` state.

- [ ] **Step 1: Write the failing tests**

  Create `backend/tests/unit/avatars/test_generation_retry.py`:

  ```python
  """Unit tests — generation_service retry backoff."""

  from __future__ import annotations

  import pytest

  from app.avatars.generation_service import _backoff_seconds


  @pytest.mark.unit
  def test_backoff_after_first_failed_attempt_is_30s() -> None:
      assert _backoff_seconds(1) == 30


  @pytest.mark.unit
  def test_backoff_after_second_failed_attempt_is_120s() -> None:
      assert _backoff_seconds(2) == 120


  @pytest.mark.unit
  def test_backoff_after_third_or_more_failed_attempts_is_480s() -> None:
      assert _backoff_seconds(3) == 480
      assert _backoff_seconds(4) == 480
      assert _backoff_seconds(10) == 480
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_generation_retry.py -v
  ```
  Expected: FAIL — `ImportError: cannot import name '_backoff_seconds' from 'app.avatars.generation_service'`.

- [ ] **Step 3: Add `_backoff_seconds` to `generation_service.py`**

  At the top of `backend/app/avatars/generation_service.py`, after the existing constants (`_MAX_ATTEMPTS`, `_IMAGE_SIZE`, etc.), add:

  ```python
  _RETRY_BACKOFF_SECONDS = [30, 120, 480]


  def _backoff_seconds(attempt_just_failed: int) -> int:
      """Return seconds to sleep before the next attempt. attempt_just_failed is 1-indexed."""
      idx = attempt_just_failed - 1
      return _RETRY_BACKOFF_SECONDS[min(idx, len(_RETRY_BACKOFF_SECONDS) - 1)]
  ```

- [ ] **Step 4: Run backoff tests to verify they pass**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_generation_retry.py -v
  ```
  Expected: PASS 3/3.

- [ ] **Step 5: Write the failing tests for retry state transitions**

  Add these tests to `backend/tests/unit/avatars/test_generation_retry.py`:

  ```python
  import asyncio
  import uuid
  from unittest.mock import AsyncMock, MagicMock, patch


  @pytest.mark.unit
  @pytest.mark.asyncio
  async def test_run_generation_job_skips_complete_jobs() -> None:
      job_id = uuid.uuid4()
      mock_job = MagicMock()
      mock_job.status = "complete"

      mock_repo = AsyncMock()
      mock_repo.get_job.return_value = mock_job

      with patch(
          "app.avatars.generation_service.SQLAlchemyAvatarRepository",
          return_value=mock_repo,
      ), patch(
          "app.avatars.generation_service.create_async_engine"
      ), patch(
          "app.avatars.generation_service.AsyncSession"
      ) as mock_session_cls:
          mock_session = AsyncMock()
          mock_session.__aenter__ = AsyncMock(return_value=mock_session)
          mock_session.__aexit__ = AsyncMock(return_value=False)
          mock_begin = AsyncMock()
          mock_begin.__aenter__ = AsyncMock(return_value=mock_begin)
          mock_begin.__aexit__ = AsyncMock(return_value=False)
          mock_session.begin.return_value = mock_begin
          mock_session_cls.return_value = mock_session

          with patch(
              "app.avatars.generation_service._run_pipeline"
          ) as mock_pipeline:
              from app.avatars.generation_service import run_generation_job

              await run_generation_job(job_id)
              mock_pipeline.assert_not_called()


  @pytest.mark.unit
  @pytest.mark.asyncio
  async def test_run_generation_job_processes_retrying_jobs() -> None:
      job_id = uuid.uuid4()
      mock_job = MagicMock()
      mock_job.status = "retrying"
      mock_avatar = MagicMock()

      mock_repo = AsyncMock()
      mock_repo.get_job.return_value = mock_job
      mock_repo.get.return_value = mock_avatar

      with patch(
          "app.avatars.generation_service.SQLAlchemyAvatarRepository",
          return_value=mock_repo,
      ), patch(
          "app.avatars.generation_service.create_async_engine"
      ), patch(
          "app.avatars.generation_service.AsyncSession"
      ) as mock_session_cls:
          mock_session = AsyncMock()
          mock_session.__aenter__ = AsyncMock(return_value=mock_session)
          mock_session.__aexit__ = AsyncMock(return_value=False)
          mock_begin = AsyncMock()
          mock_begin.__aenter__ = AsyncMock(return_value=mock_begin)
          mock_begin.__aexit__ = AsyncMock(return_value=False)
          mock_session.begin.return_value = mock_begin
          mock_session_cls.return_value = mock_session

          with patch(
              "app.avatars.generation_service._run_pipeline"
          ) as mock_pipeline:
              mock_pipeline.return_value = None
              from app.avatars.generation_service import run_generation_job

              await run_generation_job(job_id)
              mock_pipeline.assert_called_once()
  ```

- [ ] **Step 6: Run new tests to verify they fail**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_generation_retry.py::test_run_generation_job_skips_complete_jobs tests/unit/avatars/test_generation_retry.py::test_run_generation_job_processes_retrying_jobs -v
  ```
  Expected: the `_processes_retrying_jobs` test FAILS (current code rejects `retrying` status); the `_skips_complete_jobs` test should PASS or FAIL depending on current logic — note the result.

- [ ] **Step 7: Update `run_generation_job` to accept `retrying` status**

  In `backend/app/avatars/generation_service.py`, in `run_generation_job`, find:

  ```python
  if job.status not in ("queued", "generating"):
  ```

  Replace with:

  ```python
  if job.status not in ("queued", "generating", "retrying"):
  ```

- [ ] **Step 8: Update `_run_pipeline` to set `retrying` status + backoff between attempts**

  In `_run_pipeline`, the `for attempt in range(1, _MAX_ATTEMPTS + 1):` loop currently ends each failed iteration and immediately moves to the next attempt. After the `except Exception` block (inside the loop), add the retry sleep before continuing. Also change the final failure status from `"failed"` to `"permanent_failure"`.

  Find the `except Exception as exc:` block inside the loop (it ends with `logger.warning(...)`). After the `logger.warning(...)` call and BEFORE the loop continues to the next attempt, add:

  ```python
          if attempt < _MAX_ATTEMPTS:
              backoff = _backoff_seconds(attempt)
              async with AsyncSession(engine, expire_on_commit=False) as session:
                  async with session.begin():
                      repo = repo_factory(session)
                      job = await repo.get_job(job_id)
                      if job is None:
                          return
                      job.status = "retrying"
                      await repo.update_job(job)
              await asyncio.sleep(backoff)
  ```

  Then in the `# All attempts exhausted` block at the bottom of `_run_pipeline`, change:

  ```python
  job.status = "failed"
  ```

  To:

  ```python
  job.status = "permanent_failure"
  ```

  Also add `import asyncio` at the top of `generation_service.py` if not already present (check: the file does not currently import `asyncio`).

- [ ] **Step 9: Run all retry tests to verify they pass**

  ```bash
  cd backend && python -m pytest tests/unit/avatars/test_generation_retry.py -v
  ```
  Expected: PASS 5/5.

- [ ] **Step 10: Run full backend unit suite**

  ```bash
  cd backend && python -m pytest tests/unit/ -v
  ```
  Expected: all pass; no regressions.

- [ ] **Step 11: Run Black + Ruff on changed files**

  ```bash
  cd backend
  black app/avatars/generation_service.py tests/unit/avatars/test_generation_retry.py
  ruff check app/avatars/generation_service.py tests/unit/avatars/test_generation_retry.py
  ```
  Expected: no changes from Black (code already formatted); Ruff exits 0.

- [ ] **Step 12: Commit**

  ```bash
  git add backend/app/avatars/generation_service.py \
          backend/tests/unit/avatars/test_generation_retry.py
  git commit -m "feat(avatars): add exponential backoff retry with retrying/permanent_failure states"
  ```

---

### Task 3: Frontend — AvatarCard component

**Files:**
- Create: `frontend/src/features/avatar/AvatarCard.tsx`
- Create: `frontend/src/features/avatar/AvatarCard.test.tsx`

**Interfaces:**
- Consumes: `AvatarListItem` from `frontend/src/engine/avatar/types.ts` (exists).
- Produces: `<AvatarCard avatar={AvatarListItem} selected={boolean} onSelect={() => void} />` — consumed by Task 4's gallery.

The card shows:
- `portrait.small_url` image (or a "Generating…" placeholder when `status === 'pending'`)
- `avatar.name` (or species as fallback if name is null)
- A species label
- Status badge: green dot for `published`, spinning indicator for `pending`, red for `failed`/`permanent_failure`

- [ ] **Step 1: Write the failing tests**

  Create `frontend/src/features/avatar/AvatarCard.test.tsx`:

  ```tsx
  import { render, screen } from '@testing-library/react';
  import userEvent from '@testing-library/user-event';
  import { describe, expect, it, vi } from 'vitest';
  import { AvatarCard } from './AvatarCard';
  import type { AvatarListItem } from '../../engine/avatar/types';

  const published: AvatarListItem = {
    avatar_id: 'a1',
    name: 'Foxy',
    species: 'fox',
    status: 'published',
    is_favourite: false,
    portrait: {
      id: 'p1',
      version: 1,
      prompt_version: '1.0.0',
      model_version: 'dall-e-3',
      full_url: 'http://example.com/full.png',
      medium_url: 'http://example.com/medium.png',
      small_url: 'http://example.com/small.png',
      thumb_url: 'http://example.com/thumb.png',
      created_at: '2026-01-01T00:00:00Z',
    },
    created_at: '2026-01-01T00:00:00Z',
  };

  const pending: AvatarListItem = {
    avatar_id: 'a2',
    name: null,
    species: 'rabbit',
    status: 'pending',
    is_favourite: false,
    portrait: null,
    created_at: '2026-01-01T00:00:00Z',
  };

  describe('AvatarCard', () => {
    it('shows the avatar name when published', () => {
      render(<AvatarCard avatar={published} />);
      expect(screen.getByText('Foxy')).toBeInTheDocument();
    });

    it('shows species as fallback when name is null', () => {
      render(<AvatarCard avatar={{ ...published, name: null }} />);
      expect(screen.getByText(/fox/i)).toBeInTheDocument();
    });

    it('renders portrait image for published avatar', () => {
      render(<AvatarCard avatar={published} />);
      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', 'http://example.com/small.png');
    });

    it('shows generating indicator for pending avatar', () => {
      render(<AvatarCard avatar={pending} />);
      expect(screen.getByText(/generating/i)).toBeInTheDocument();
    });

    it('calls onSelect with avatar_id when clicked', async () => {
      const onSelect = vi.fn();
      const user = userEvent.setup();
      render(<AvatarCard avatar={published} onSelect={onSelect} />);
      await user.click(screen.getByRole('button'));
      expect(onSelect).toHaveBeenCalledWith('a1');
    });

    it('applies selected visual indicator when selected is true', () => {
      render(<AvatarCard avatar={published} selected />);
      const btn = screen.getByRole('button');
      expect(btn).toHaveAttribute('aria-pressed', 'true');
    });
  });
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd frontend && npx vitest run src/features/avatar/AvatarCard.test.tsx
  ```
  Expected: FAIL — cannot find module `./AvatarCard`.

- [ ] **Step 3: Create `frontend/src/features/avatar/AvatarCard.tsx`**

  ```tsx
  import tokens from '../../shared/tokens';
  import type { AvatarListItem } from '../../engine/avatar/types';

  interface AvatarCardProps {
    avatar: AvatarListItem;
    selected?: boolean;
    onSelect?: (avatarId: string) => void;
  }

  export function AvatarCard({ avatar, selected = false, onSelect }: AvatarCardProps) {
    const isPending = avatar.status === 'pending';
    const isFailed = avatar.status === 'failed' || avatar.status === 'permanent_failure';
    const displayName = avatar.name ?? avatar.species;

    const cardStyle: React.CSSProperties = {
      background: tokens.color.surface,
      borderRadius: tokens.radius.lg,
      padding: tokens.spacing.md,
      boxShadow: selected ? `0 0 0 3px ${tokens.color.primary}` : tokens.shadow.card,
      cursor: onSelect ? 'pointer' : 'default',
      border: 'none',
      textAlign: 'left',
      width: '100%',
      transition: `box-shadow ${tokens.animation.quick}`,
    };

    const content = (
      <>
        {isPending ? (
          <div
            aria-label="generating"
            style={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: tokens.color.border,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: tokens.spacing.sm,
            }}
          >
            <span
              aria-hidden="true"
              style={{
                fontSize: 24,
                animation: 'spin 1s linear infinite',
              }}
            >
              ⏳
            </span>
          </div>
        ) : (
          <img
            src={avatar.portrait?.small_url}
            alt={displayName}
            style={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              objectFit: 'cover',
              marginBottom: tokens.spacing.sm,
            }}
          />
        )}
        <div style={{ fontWeight: 600, color: tokens.color.textPrimary }}>{displayName}</div>
        <div style={{ fontSize: 14, color: tokens.color.textSecondary, textTransform: 'capitalize' }}>
          {avatar.species}
        </div>
        {isPending && (
          <div style={{ fontSize: 12, color: tokens.color.primary, marginTop: tokens.spacing.xs }}>
            Generating…
          </div>
        )}
        {isFailed && (
          <div style={{ fontSize: 12, color: tokens.color.error, marginTop: tokens.spacing.xs }}>
            Hmm, something went wobbly.
          </div>
        )}
      </>
    );

    if (onSelect) {
      return (
        <button
          type="button"
          style={cardStyle}
          aria-pressed={selected}
          onClick={() => onSelect(avatar.avatar_id)}
          onFocus={(e) => {
            (e.currentTarget as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
            (e.currentTarget as HTMLElement).style.outlineOffset = '2px';
          }}
          onBlur={(e) => {
            (e.currentTarget as HTMLElement).style.outline = 'none';
          }}
        >
          {content}
        </button>
      );
    }

    return <div style={cardStyle}>{content}</div>;
  }
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  cd frontend && npx vitest run src/features/avatar/AvatarCard.test.tsx
  ```
  Expected: PASS 6/6.

- [ ] **Step 5: Run Prettier**

  ```bash
  cd frontend && npx prettier --write src/features/avatar/AvatarCard.tsx src/features/avatar/AvatarCard.test.tsx
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add frontend/src/features/avatar/AvatarCard.tsx \
          frontend/src/features/avatar/AvatarCard.test.tsx
  git commit -m "feat(frontend): add AvatarCard component"
  ```

---

### Task 4: Frontend — `useAvatarGallery` hook + AvatarGalleryPage

**Files:**
- Create: `frontend/src/features/avatar/useAvatarGallery.ts`
- Create: `frontend/src/features/avatar/useAvatarGallery.test.ts`
- Modify: `frontend/src/pages/AvatarGalleryPage.tsx`
- Create: `frontend/src/pages/AvatarGalleryPage.test.tsx`

**Interfaces:**
- Consumes: `listAvatars(): Promise<AvatarListItem[]>` from `frontend/src/engine/avatar/avatarApi.ts` (exists); `AvatarListItem` from `types.ts` (exists); `AvatarCard` from Task 3.
- Produces: `useAvatarGallery(): { avatars: AvatarListItem[], loading: boolean, error: string | null }` — consumed by `AvatarGalleryPage`.

**Hook behaviour:**
- On mount: call `listAvatars()`. Set `loading = false` when done.
- If any avatar has `status === 'pending'`: start a 3-second interval that re-calls `listAvatars()`. Clear the interval when no avatars are pending (all are `published`, `failed`, or `permanent_failure`).
- On unmount: clear the interval.
- `error` is set to child-friendly message `'Looks like we lost the signal. Check your connection!'` on fetch failure.

- [ ] **Step 1: Write the failing hook tests (covers Review Focus items 2, 4, 5)**

  Create `frontend/src/features/avatar/useAvatarGallery.test.ts`:

  ```typescript
  import { act, renderHook, waitFor } from '@testing-library/react';
  import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
  import * as avatarApiModule from '../../engine/avatar/avatarApi';
  import { useAvatarGallery } from './useAvatarGallery';
  import type { AvatarListItem } from '../../engine/avatar/types';

  vi.mock('../../engine/avatar/avatarApi');

  const published: AvatarListItem = {
    avatar_id: 'a1',
    name: 'Foxy',
    species: 'fox',
    status: 'published',
    is_favourite: false,
    portrait: null,
    created_at: '2026-01-01T00:00:00Z',
  };

  const pending: AvatarListItem = {
    avatar_id: 'a2',
    name: null,
    species: 'rabbit',
    status: 'pending',
    is_favourite: false,
    portrait: null,
    created_at: '2026-01-01T00:00:00Z',
  };

  describe('useAvatarGallery', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });
    afterEach(() => {
      vi.useRealTimers();
      vi.clearAllMocks();
    });

    it('returns loaded avatars after initial fetch', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
      const { result } = renderHook(() => useAvatarGallery());
      expect(result.current.loading).toBe(true);
      await waitFor(() => expect(result.current.loading).toBe(false));
      expect(result.current.avatars).toHaveLength(1);
      expect(result.current.avatars[0].avatar_id).toBe('a1');
    });

    it('does NOT start polling when all avatars are published', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
      const setIntervalSpy = vi.spyOn(global, 'setInterval');
      const { result } = renderHook(() => useAvatarGallery());
      await waitFor(() => expect(result.current.loading).toBe(false));
      expect(setIntervalSpy).not.toHaveBeenCalled();
    });

    it('starts polling when an avatar is pending', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([pending]);
      const setIntervalSpy = vi.spyOn(global, 'setInterval');
      const { result } = renderHook(() => useAvatarGallery());
      await waitFor(() => expect(result.current.loading).toBe(false));
      expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 3000);
    });

    it('stops polling when re-fetch returns no pending avatars', async () => {
      vi.mocked(avatarApiModule.listAvatars)
        .mockResolvedValueOnce([pending])
        .mockResolvedValue([published]);
      const clearIntervalSpy = vi.spyOn(global, 'clearInterval');
      const { result } = renderHook(() => useAvatarGallery());
      await waitFor(() => expect(result.current.loading).toBe(false));

      await act(async () => {
        vi.advanceTimersByTime(3000);
      });
      await waitFor(() =>
        expect(result.current.avatars.every((a) => a.status !== 'pending')).toBe(true),
      );
      expect(clearIntervalSpy).toHaveBeenCalled();
    });

    it('sets child-friendly error message on fetch failure', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockRejectedValue(new Error('Network error'));
      const { result } = renderHook(() => useAvatarGallery());
      await waitFor(() => expect(result.current.loading).toBe(false));
      expect(result.current.error).toBe(
        'Looks like we lost the signal. Check your connection!',
      );
    });
  });
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd frontend && npx vitest run src/features/avatar/useAvatarGallery.test.ts
  ```
  Expected: FAIL — cannot find module `./useAvatarGallery`.

- [ ] **Step 3: Create `frontend/src/features/avatar/useAvatarGallery.ts`**

  ```typescript
  import { useCallback, useEffect, useRef, useState } from 'react';
  import { listAvatars } from '../../engine/avatar/avatarApi';
  import type { AvatarListItem } from '../../engine/avatar/types';

  export function useAvatarGallery() {
    const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const fetchAvatars = useCallback(async (fromPoll = false) => {
      try {
        const data = await listAvatars();
        setAvatars(data);
        if (!fromPoll) setLoading(false);

        const hasPending = data.some((a) => a.status === 'pending');
        if (hasPending && !intervalRef.current) {
          intervalRef.current = setInterval(() => {
            void fetchAvatars(true);
          }, 3000);
        } else if (!hasPending && intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          if (fromPoll) setLoading(false);
        }
      } catch {
        setError('Looks like we lost the signal. Check your connection!');
        setLoading(false);
      }
    }, []);

    useEffect(() => {
      void fetchAvatars();
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      };
    }, [fetchAvatars]);

    return { avatars, loading, error };
  }
  ```

- [ ] **Step 4: Run hook tests to verify they pass**

  ```bash
  cd frontend && npx vitest run src/features/avatar/useAvatarGallery.test.ts
  ```
  Expected: PASS 5/5.

- [ ] **Step 5: Write the failing page tests (covers Review Focus item 4)**

  Create `frontend/src/pages/AvatarGalleryPage.test.tsx`:

  ```tsx
  import { render, screen } from '@testing-library/react';
  import { MemoryRouter } from 'react-router-dom';
  import { beforeEach, describe, expect, it, vi } from 'vitest';
  import * as avatarApiModule from '../engine/avatar/avatarApi';
  import AvatarGalleryPage from './AvatarGalleryPage';
  import type { AvatarListItem } from '../engine/avatar/types';

  vi.mock('../engine/avatar/avatarApi');

  const published: AvatarListItem = {
    avatar_id: 'a1',
    name: 'Foxy',
    species: 'fox',
    status: 'published',
    is_favourite: false,
    portrait: {
      id: 'p1',
      version: 1,
      prompt_version: '1.0.0',
      model_version: 'dall-e-3',
      full_url: 'http://x.com/full.png',
      medium_url: 'http://x.com/medium.png',
      small_url: 'http://x.com/small.png',
      thumb_url: 'http://x.com/thumb.png',
      created_at: '2026-01-01T00:00:00Z',
    },
    created_at: '2026-01-01T00:00:00Z',
  };

  const pending: AvatarListItem = {
    avatar_id: 'a2',
    name: null,
    species: 'rabbit',
    status: 'pending',
    is_favourite: false,
    portrait: null,
    created_at: '2026-01-01T00:00:00Z',
  };

  describe('AvatarGalleryPage', () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.clearAllMocks();
    });
    afterEach(() => {
      vi.useRealTimers();
    });

    it('shows empty state with create CTA when no avatars', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([]);
      render(<MemoryRouter><AvatarGalleryPage /></MemoryRouter>);
      expect(await screen.findByRole('link', { name: /create your first avatar/i })).toBeInTheDocument();
    });

    it('renders avatar cards when avatars exist', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
      render(<MemoryRouter><AvatarGalleryPage /></MemoryRouter>);
      expect(await screen.findByText('Foxy')).toBeInTheDocument();
    });

    it('shows generating card (not empty state) when only avatar is pending', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([pending]);
      render(<MemoryRouter><AvatarGalleryPage /></MemoryRouter>);
      expect(await screen.findByText(/generating/i)).toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /create your first avatar/i })).toBeNull();
    });

    it('shows error state on fetch failure', async () => {
      vi.mocked(avatarApiModule.listAvatars).mockRejectedValue(new Error('oops'));
      render(<MemoryRouter><AvatarGalleryPage /></MemoryRouter>);
      expect(await screen.findByRole('alert')).toBeInTheDocument();
    });
  });
  ```

- [ ] **Step 6: Run page tests to verify they fail**

  ```bash
  cd frontend && npx vitest run src/pages/AvatarGalleryPage.test.tsx
  ```
  Expected: FAIL — current page is a stub.

- [ ] **Step 7: Implement `frontend/src/pages/AvatarGalleryPage.tsx`**

  ```tsx
  import { useNavigate } from 'react-router-dom';
  import { AvatarCard } from '../features/avatar/AvatarCard';
  import { useAvatarGallery } from '../features/avatar/useAvatarGallery';
  import { Button } from '../shared/components/Button';
  import { ErrorState } from '../shared/components/ErrorState';
  import { LoadingSpinner } from '../shared/components/LoadingSpinner';
  import tokens from '../shared/tokens';
  import avatarGenerationImg from '../../assets/avatar_generation.jpeg';

  export default function AvatarGalleryPage() {
    const { avatars, loading, error } = useAvatarGallery();
    const navigate = useNavigate();

    if (loading) return <LoadingSpinner />;

    if (error) {
      return (
        <div role="alert" style={{ padding: tokens.spacing.xl }}>
          <ErrorState message={error} />
        </div>
      );
    }

    if (avatars.length === 0) {
      return (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: tokens.spacing.lg,
            padding: tokens.spacing.xl,
          }}
        >
          <img
            src={avatarGenerationImg}
            alt=""
            aria-hidden="true"
            style={{ maxWidth: 320, borderRadius: tokens.radius.lg }}
          />
          <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
          <p style={{ color: tokens.color.textSecondary }}>
            You don&apos;t have any avatars yet. Create your first one!
          </p>
          <Button
            variant="primary"
            onClick={() => void navigate('/avatars/new')}
          >
            <a
              href="/avatars/new"
              style={{ color: 'inherit', textDecoration: 'none' }}
              onClick={(e) => {
                e.preventDefault();
                void navigate('/avatars/new');
              }}
            >
              Create Your First Avatar
            </a>
          </Button>
        </div>
      );
    }

    return (
      <div style={{ padding: tokens.spacing.xl }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: tokens.spacing.lg,
          }}
        >
          <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
          <Button variant="primary" onClick={() => void navigate('/avatars/new')}>
            + New Avatar
          </Button>
        </div>
        <div
          role="list"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
            gap: tokens.spacing.md,
          }}
        >
          {avatars.map((avatar) => (
            <div key={avatar.avatar_id} role="listitem">
              <AvatarCard avatar={avatar} />
            </div>
          ))}
        </div>
      </div>
    );
  }
  ```

  **Note on the empty-state CTA button:** Testing Library's `getByRole('link')` works on `<a>` elements. The "Create Your First Avatar" CTA must render as an `<a>` tag (or wrap an `<a>`) so the test can find it by role. Wrap the navigate call as shown above, or replace the Button with a plain `<Link>` component from react-router-dom if that is simpler. Either works as long as the test passes.

- [ ] **Step 8: Run page tests to verify they pass**

  ```bash
  cd frontend && npx vitest run src/pages/AvatarGalleryPage.test.tsx
  ```
  Expected: PASS 4/4.

- [ ] **Step 9: Run full frontend test suite**

  ```bash
  cd frontend && npx vitest run
  ```
  Expected: all pass.

- [ ] **Step 10: Run Prettier**

  ```bash
  cd frontend && npx prettier --write \
    src/features/avatar/useAvatarGallery.ts \
    src/features/avatar/useAvatarGallery.test.ts \
    src/pages/AvatarGalleryPage.tsx \
    src/pages/AvatarGalleryPage.test.tsx
  ```

- [ ] **Step 11: Commit**

  ```bash
  git add \
    frontend/src/features/avatar/useAvatarGallery.ts \
    frontend/src/features/avatar/useAvatarGallery.test.ts \
    frontend/src/pages/AvatarGalleryPage.tsx \
    frontend/src/pages/AvatarGalleryPage.test.tsx
  git commit -m "feat(frontend): implement AvatarGalleryPage with polling"
  ```

---

### Task 5: Frontend — Avatar Creator Wizard (5-step)

**Files:**
- Modify: `frontend/src/pages/AvatarCreatorPage.tsx`
- Create: `frontend/src/pages/AvatarCreatorPage.test.tsx`

**Interfaces:**
- Consumes: `createAvatar(data: CreateAvatarRequest): Promise<AvatarCreationResponse>` and `pollGenerationJob(avatarId, jobId): Promise<JobStatusResponse>` from `frontend/src/engine/avatar/avatarApi.ts` (both exist); `JobStatus`, `AvatarCreationResponse`, `CreateAvatarRequest` from `types.ts`; `Button` from `shared/components/Button.tsx`; `LoadingSpinner` from `shared/components/LoadingSpinner.tsx`.

**Wizard steps:**
1. **Species** — pick one of: `fox`, `rabbit`, `bear`, `cat`, `mouse`, `panda`
2. **Colour** — pick fur color from palette (6 swatches) + eye color from palette (6 swatches)
3. **Style** — pick hairstyle (`short`, `long`, `curly`, `braided`) + optional accessories multi-select (`headband`, `glasses`, `hat`, `scarf`)
4. **Clothing** — pick top color (8 swatches) + bottom color (8 swatches)
5. **Reveal** — calls `createAvatar()`, polls `pollGenerationJob()` every 3 s until `status === 'complete'` or terminal failure; navigates to `/avatars` on success

**Palettes (use these exact values):**

```typescript
const FUR_COLORS = ['#D2691E','#F4A460','#8B4513','#FFFDD0','#808080','#1C1C1C'];
const EYE_COLORS = ['#4B0082','#228B22','#0000CD','#8B0000','#FF8C00','#A9A9A9'];
const CLOTHES_COLORS = ['#4169E1','#DC143C','#228B22','#FF8C00','#800080','#FFD700','#FFFFFF','#1C1C1C'];
```

**Terminal job statuses** (stop polling when reached): `'complete'`, `'failed'`, `'permanent_failure'`.

- [ ] **Step 1: Write the failing tests (covers Review Focus item 3)**

  Create `frontend/src/pages/AvatarCreatorPage.test.tsx`:

  ```tsx
  import { render, screen, waitFor } from '@testing-library/react';
  import userEvent from '@testing-library/user-event';
  import { MemoryRouter } from 'react-router-dom';
  import { beforeEach, describe, expect, it, vi } from 'vitest';
  import * as avatarApiModule from '../engine/avatar/avatarApi';
  import AvatarCreatorPage from './AvatarCreatorPage';

  vi.mock('../engine/avatar/avatarApi');

  const mockNavigate = vi.fn();
  vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
      ...(actual as object),
      useNavigate: () => mockNavigate,
    };
  });

  describe('AvatarCreatorPage', () => {
    beforeEach(() => {
      vi.clearAllMocks();
      vi.useFakeTimers();
    });
    afterEach(() => {
      vi.useRealTimers();
    });

    it('shows species selection on step 1', () => {
      render(<MemoryRouter><AvatarCreatorPage /></MemoryRouter>);
      expect(screen.getByRole('heading', { name: /choose your animal/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /fox/i })).toBeInTheDocument();
    });

    it('advancing to step 2 shows colour picker', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<MemoryRouter><AvatarCreatorPage /></MemoryRouter>);
      await user.click(screen.getByRole('button', { name: /fox/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      expect(screen.getByRole('heading', { name: /choose colours/i })).toBeInTheDocument();
    });

    it('going back from step 2 preserves species selection', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<MemoryRouter><AvatarCreatorPage /></MemoryRouter>);
      await user.click(screen.getByRole('button', { name: /fox/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      await user.click(screen.getByRole('button', { name: /back/i }));
      // fox button should still appear as selected (aria-pressed true)
      expect(screen.getByRole('button', { name: /fox/i })).toHaveAttribute('aria-pressed', 'true');
    });

    it('step 5 calls createAvatar and polls until complete then navigates', async () => {
      vi.mocked(avatarApiModule.createAvatar).mockResolvedValue({
        avatar_id: 'a1',
        job_id: 'j1',
        status: 'queued',
      });
      vi.mocked(avatarApiModule.pollGenerationJob)
        .mockResolvedValueOnce({
          job_id: 'j1',
          avatar_id: 'a1',
          status: 'generating',
          attempt: 1,
          error: null,
          created_at: '2026-01-01T00:00:00Z',
          completed_at: null,
        })
        .mockResolvedValue({
          job_id: 'j1',
          avatar_id: 'a1',
          status: 'complete',
          attempt: 1,
          error: null,
          created_at: '2026-01-01T00:00:00Z',
          completed_at: '2026-01-01T00:01:00Z',
        });

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<MemoryRouter><AvatarCreatorPage /></MemoryRouter>);

      // Step 1: species
      await user.click(screen.getByRole('button', { name: /fox/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      // Step 2: colour — just click Next (defaults are fine)
      await user.click(screen.getByRole('button', { name: /next/i }));
      // Step 3: style — just click Next
      await user.click(screen.getByRole('button', { name: /next/i }));
      // Step 4: clothing — just click Next
      await user.click(screen.getByRole('button', { name: /next/i }));
      // Step 5: reveal — createAvatar is called automatically
      await waitFor(() => expect(avatarApiModule.createAvatar).toHaveBeenCalledTimes(1));

      // Advance timer to trigger second poll
      await vi.advanceTimersByTimeAsync(3000);
      await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/avatars'));
    });

    it('shows friendly error message when generation permanently fails', async () => {
      vi.mocked(avatarApiModule.createAvatar).mockResolvedValue({
        avatar_id: 'a1',
        job_id: 'j1',
        status: 'queued',
      });
      vi.mocked(avatarApiModule.pollGenerationJob).mockResolvedValue({
        job_id: 'j1',
        avatar_id: 'a1',
        status: 'permanent_failure',
        attempt: 3,
        error: 'Generation failed',
        created_at: '2026-01-01T00:00:00Z',
        completed_at: '2026-01-01T00:01:00Z',
      });

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<MemoryRouter><AvatarCreatorPage /></MemoryRouter>);

      // Navigate through all steps to reveal
      await user.click(screen.getByRole('button', { name: /fox/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => expect(avatarApiModule.createAvatar).toHaveBeenCalledTimes(1));
      await waitFor(() =>
        expect(screen.getByText(/went wobbly/i)).toBeInTheDocument(),
      );
    });
  });
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd frontend && npx vitest run src/pages/AvatarCreatorPage.test.tsx
  ```
  Expected: FAIL — current page is a stub.

- [ ] **Step 3: Implement `frontend/src/pages/AvatarCreatorPage.tsx`**

  ```tsx
  import { useCallback, useEffect, useRef, useState } from 'react';
  import { useNavigate } from 'react-router-dom';
  import { createAvatar, pollGenerationJob } from '../engine/avatar/avatarApi';
  import type { CreateAvatarRequest } from '../engine/avatar/types';
  import { Button } from '../shared/components/Button';
  import { LoadingSpinner } from '../shared/components/LoadingSpinner';
  import tokens from '../shared/tokens';

  const SPECIES = ['fox', 'rabbit', 'bear', 'cat', 'mouse', 'panda'] as const;
  const HAIRSTYLES = ['short', 'long', 'curly', 'braided'] as const;
  const ACCESSORIES_OPTIONS = ['headband', 'glasses', 'hat', 'scarf'] as const;
  const FUR_COLORS = ['#D2691E', '#F4A460', '#8B4513', '#FFFDD0', '#808080', '#1C1C1C'];
  const EYE_COLORS = ['#4B0082', '#228B22', '#0000CD', '#8B0000', '#FF8C00', '#A9A9A9'];
  const CLOTHES_COLORS = [
    '#4169E1', '#DC143C', '#228B22', '#FF8C00',
    '#800080', '#FFD700', '#FFFFFF', '#1C1C1C',
  ];

  const TERMINAL_STATUSES = new Set(['complete', 'failed', 'permanent_failure']);

  interface WizardState {
    step: 1 | 2 | 3 | 4 | 5;
    species: string;
    furColor: string;
    eyeColor: string;
    hairstyle: string;
    accessories: string[];
    topColor: string;
    bottomColor: string;
  }

  function ColorSwatch({
    color,
    selected,
    onSelect,
    label,
  }: {
    color: string;
    selected: boolean;
    onSelect: (c: string) => void;
    label: string;
  }) {
    return (
      <button
        type="button"
        aria-label={label}
        aria-pressed={selected}
        onClick={() => onSelect(color)}
        style={{
          width: 36,
          height: 36,
          borderRadius: '50%',
          background: color,
          border: selected ? `3px solid ${tokens.color.primary}` : `2px solid ${tokens.color.border}`,
          cursor: 'pointer',
          outline: 'none',
        }}
        onFocus={(e) => {
          (e.currentTarget as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
        }}
        onBlur={(e) => {
          (e.currentTarget as HTMLElement).style.outline = 'none';
        }}
      />
    );
  }

  export default function AvatarCreatorPage() {
    const navigate = useNavigate();
    const [wizard, setWizard] = useState<WizardState>({
      step: 1,
      species: '',
      furColor: FUR_COLORS[0],
      eyeColor: EYE_COLORS[0],
      hairstyle: 'short',
      accessories: [],
      topColor: CLOTHES_COLORS[0],
      bottomColor: CLOTHES_COLORS[7],
    });
    const [genError, setGenError] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const set = <K extends keyof WizardState>(key: K, val: WizardState[K]) =>
      setWizard((w) => ({ ...w, [key]: val }));

    const next = () => setWizard((w) => ({ ...w, step: (w.step + 1) as WizardState['step'] }));
    const back = () => setWizard((w) => ({ ...w, step: (w.step - 1) as WizardState['step'] }));

    const toggleAccessory = (acc: string) =>
      setWizard((w) => ({
        ...w,
        accessories: w.accessories.includes(acc)
          ? w.accessories.filter((a) => a !== acc)
          : [...w.accessories, acc],
      }));

    const startGeneration = useCallback(async () => {
      setIsGenerating(true);
      setGenError(null);
      try {
        const req: CreateAvatarRequest = {
          species: wizard.species || 'fox',
          fur_color: wizard.furColor,
          eye_color: wizard.eyeColor,
          hairstyle: wizard.hairstyle,
          accessories: wizard.accessories,
          clothes_top_color: wizard.topColor,
          clothes_bottom_color: wizard.bottomColor,
        };
        const { avatar_id, job_id } = await createAvatar(req);

        pollRef.current = setInterval(async () => {
          try {
            const job = await pollGenerationJob(avatar_id, job_id);
            if (job.status === 'complete') {
              if (pollRef.current) clearInterval(pollRef.current);
              void navigate('/avatars');
            } else if (TERMINAL_STATUSES.has(job.status) && job.status !== 'complete') {
              if (pollRef.current) clearInterval(pollRef.current);
              setIsGenerating(false);
              setGenError('Hmm, something went wobbly. Let\'s try again!');
            }
          } catch {
            if (pollRef.current) clearInterval(pollRef.current);
            setIsGenerating(false);
            setGenError('Looks like we lost the signal. Check your connection!');
          }
        }, 3000);
      } catch {
        setIsGenerating(false);
        setGenError('Hmm, something went wobbly. Let\'s try again!');
      }
    }, [wizard, navigate]);

    useEffect(() => {
      if (wizard.step === 5) {
        void startGeneration();
      }
      return () => {
        if (pollRef.current) clearInterval(pollRef.current);
      };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [wizard.step]);

    const containerStyle: React.CSSProperties = {
      maxWidth: 480,
      margin: '0 auto',
      padding: tokens.spacing.xl,
    };

    const headingStyle: React.CSSProperties = {
      color: tokens.color.textPrimary,
      marginBottom: tokens.spacing.lg,
    };

    const navStyle: React.CSSProperties = {
      display: 'flex',
      justifyContent: 'space-between',
      marginTop: tokens.spacing.xl,
    };

    if (wizard.step === 1) {
      return (
        <div style={containerStyle}>
          <h1 style={headingStyle}>Choose Your Animal</h1>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: tokens.spacing.sm }}>
            {SPECIES.map((sp) => (
              <button
                key={sp}
                type="button"
                aria-pressed={wizard.species === sp}
                onClick={() => set('species', sp)}
                style={{
                  padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
                  borderRadius: tokens.radius.md,
                  border: wizard.species === sp
                    ? `2px solid ${tokens.color.primary}`
                    : `2px solid ${tokens.color.border}`,
                  background: wizard.species === sp ? tokens.color.primary : tokens.color.surface,
                  color: wizard.species === sp ? tokens.color.textOnPrimary : tokens.color.textPrimary,
                  cursor: 'pointer',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                }}
              >
                {sp}
              </button>
            ))}
          </div>
          <div style={navStyle}>
            <span />
            <Button
              variant="primary"
              disabled={!wizard.species}
              onClick={next}
            >
              Next
            </Button>
          </div>
        </div>
      );
    }

    if (wizard.step === 2) {
      return (
        <div style={containerStyle}>
          <h1 style={headingStyle}>Choose Colours</h1>
          <p style={{ color: tokens.color.textSecondary }}>Fur colour</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap', marginBottom: tokens.spacing.md }}>
            {FUR_COLORS.map((c) => (
              <ColorSwatch key={c} color={c} selected={wizard.furColor === c} onSelect={(v) => set('furColor', v)} label={`Fur colour ${c}`} />
            ))}
          </div>
          <p style={{ color: tokens.color.textSecondary }}>Eye colour</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
            {EYE_COLORS.map((c) => (
              <ColorSwatch key={c} color={c} selected={wizard.eyeColor === c} onSelect={(v) => set('eyeColor', v)} label={`Eye colour ${c}`} />
            ))}
          </div>
          <div style={navStyle}>
            <Button variant="secondary" onClick={back}>Back</Button>
            <Button variant="primary" onClick={next}>Next</Button>
          </div>
        </div>
      );
    }

    if (wizard.step === 3) {
      return (
        <div style={containerStyle}>
          <h1 style={headingStyle}>Choose Your Style</h1>
          <p style={{ color: tokens.color.textSecondary }}>Hairstyle</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap', marginBottom: tokens.spacing.md }}>
            {HAIRSTYLES.map((h) => (
              <button
                key={h}
                type="button"
                aria-pressed={wizard.hairstyle === h}
                onClick={() => set('hairstyle', h)}
                style={{
                  padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
                  borderRadius: tokens.radius.md,
                  border: wizard.hairstyle === h
                    ? `2px solid ${tokens.color.primary}`
                    : `2px solid ${tokens.color.border}`,
                  background: wizard.hairstyle === h ? tokens.color.primary : tokens.color.surface,
                  color: wizard.hairstyle === h ? tokens.color.textOnPrimary : tokens.color.textPrimary,
                  cursor: 'pointer',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                }}
              >
                {h}
              </button>
            ))}
          </div>
          <p style={{ color: tokens.color.textSecondary }}>Accessories (optional)</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
            {ACCESSORIES_OPTIONS.map((acc) => (
              <button
                key={acc}
                type="button"
                aria-pressed={wizard.accessories.includes(acc)}
                onClick={() => toggleAccessory(acc)}
                style={{
                  padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
                  borderRadius: tokens.radius.md,
                  border: wizard.accessories.includes(acc)
                    ? `2px solid ${tokens.color.primary}`
                    : `2px solid ${tokens.color.border}`,
                  background: wizard.accessories.includes(acc) ? tokens.color.primary : tokens.color.surface,
                  color: wizard.accessories.includes(acc) ? tokens.color.textOnPrimary : tokens.color.textPrimary,
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                }}
              >
                {acc}
              </button>
            ))}
          </div>
          <div style={navStyle}>
            <Button variant="secondary" onClick={back}>Back</Button>
            <Button variant="primary" onClick={next}>Next</Button>
          </div>
        </div>
      );
    }

    if (wizard.step === 4) {
      return (
        <div style={containerStyle}>
          <h1 style={headingStyle}>Choose Clothing</h1>
          <p style={{ color: tokens.color.textSecondary }}>Top colour</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap', marginBottom: tokens.spacing.md }}>
            {CLOTHES_COLORS.map((c) => (
              <ColorSwatch key={c} color={c} selected={wizard.topColor === c} onSelect={(v) => set('topColor', v)} label={`Top colour ${c}`} />
            ))}
          </div>
          <p style={{ color: tokens.color.textSecondary }}>Shorts colour</p>
          <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
            {CLOTHES_COLORS.map((c) => (
              <ColorSwatch key={c} color={c} selected={wizard.bottomColor === c} onSelect={(v) => set('bottomColor', v)} label={`Shorts colour ${c}`} />
            ))}
          </div>
          <div style={navStyle}>
            <Button variant="secondary" onClick={back}>Back</Button>
            <Button variant="primary" onClick={next}>Next</Button>
          </div>
        </div>
      );
    }

    // Step 5: Reveal / generation
    if (genError) {
      return (
        <div style={containerStyle}>
          <p style={{ color: tokens.color.error }}>{genError}</p>
          <div style={navStyle}>
            <Button variant="secondary" onClick={back}>Back</Button>
            <Button variant="primary" onClick={() => { setGenError(null); void startGeneration(); }}>
              Try Again
            </Button>
          </div>
        </div>
      );
    }

    return (
      <div style={{ ...containerStyle, textAlign: 'center' }}>
        <h1 style={headingStyle}>Creating Your Avatar…</h1>
        <LoadingSpinner />
        <p style={{ color: tokens.color.textSecondary, marginTop: tokens.spacing.md }}>
          Our AI artist is painting your character. This takes about 20 seconds.
        </p>
      </div>
    );
  }
  ```

  **Button variant note:** The current `Button` component uses `variant: 'primary'`. Check `frontend/src/shared/components/Button.tsx` — if it does not support `variant: 'secondary'`, replace all `variant="secondary"` with `variant="primary"` and style the Back buttons differently, or add `secondary` support to `Button.tsx` (just sets a lighter background). Do not break existing tests.

- [ ] **Step 4: Run page tests to verify they pass**

  ```bash
  cd frontend && npx vitest run src/pages/AvatarCreatorPage.test.tsx
  ```
  Expected: PASS 5/5.

- [ ] **Step 5: Run full frontend test suite**

  ```bash
  cd frontend && npx vitest run
  ```
  Expected: all pass.

- [ ] **Step 6: Run TypeScript check**

  ```bash
  cd frontend && npx tsc --noEmit
  ```
  Expected: no errors.

- [ ] **Step 7: Run Prettier**

  ```bash
  cd frontend && npx prettier --write \
    src/pages/AvatarCreatorPage.tsx \
    src/pages/AvatarCreatorPage.test.tsx
  ```

- [ ] **Step 8: Commit**

  ```bash
  git add \
    frontend/src/pages/AvatarCreatorPage.tsx \
    frontend/src/pages/AvatarCreatorPage.test.tsx
  git commit -m "feat(frontend): implement 5-step AvatarCreatorPage wizard"
  ```

---

## Self-Review

### 1. Spec coverage

| Spec requirement | Task |
|-----------------|------|
| `retrying` / `permanent_failure` states | Task 1 |
| Exponential backoff 30s / 120s / 480s | Task 2 |
| Idempotency: `run_generation_job` skips complete/failed jobs | Task 2 (step 6 test) |
| Avatar Gallery page — grid, empty state, polling | Task 4 |
| Empty state = image + CTA; no blank page | Task 4 |
| Generating… skeleton card for pending avatar | Tasks 3 + 4 |
| Poll `GET /api/v1/avatars/*/jobs/*` every 3 s | Task 4 (hook), Task 5 (creator) |
| Avatar Creator — 5-step wizard | Task 5 |
| Species selection | Task 5, step 1 |
| Fur/eye colour picker | Task 5, step 2 |
| Hairstyle + accessories | Task 5, step 3 |
| Clothing colours | Task 5, step 4 |
| Reveal: generate + poll + navigate on complete | Task 5, step 5 |
| Child-friendly error messages | Tasks 4 + 5 (exact strings from spec) |
| `assets/avatar_generation.jpeg` used in empty state | Task 4 |
| Migration `0011` for DB constraint | Task 1 |

No gaps found.

### 2. Placeholder scan

No TBDs, no "add appropriate error handling", no "similar to Task N". Every code block is complete.

### 3. Type consistency

- `JobStatus` extended in Task 1; consumed in Task 5's `TERMINAL_STATUSES` set — both reference `'complete'`, `'permanent_failure'`, `'failed'` ✓
- `AvatarListItem.status` is `string` in the backend schema but `AvatarStatus = 'pending' | 'published' | 'failed'` in the frontend type — `'pending'` check in useAvatarGallery and AvatarCard is consistent with this type ✓
- `CreateAvatarRequest` fields (`fur_color`, `eye_color`, etc.) are used exactly as defined in `types.ts` ✓

### 4. Review Focus tests

All five Review Focus tests are wired into tasks:
1. Task 2 step 6: `test_run_generation_job_processes_retrying_jobs` ✓
2. Task 4 step 1: `stops polling when re-fetch returns no pending avatars` ✓
3. Task 5 step 1: `going back from step 2 preserves species selection` ✓
4. Task 4 step 5: `shows generating card (not empty state) when only avatar is pending` ✓
5. Task 4 step 1: `does NOT start polling when all avatars are published` ✓
