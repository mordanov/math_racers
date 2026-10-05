# What Claude Code Can Implement

**Status:** Reference — work backlog for the next development phase
**Date:** 2026-10-05
**Context:** Specs 001–009 are merged. Backend domain layer is complete. The frontend has
engine code only (`engine/math`, `engine/race`, `engine/achievements`, `engine/avatar`) but
zero UI. `App.tsx` is a single `<div>Math Racers</div>`. Everything below is buildable in
TypeScript/Python/React by Claude Code without external assets or API keys.

---

## 1. Backend — Remaining Spec 002 Tasks

Spec 002 (Backend Foundation) has five open task groups that were deferred past the MVP cut.

### 1.1 Child Profile Ownership Guard (T030–T031)

`GET /PATCH` endpoints in all domain modules take a `child_profile_id` parameter but the
ownership check is currently a safe stub that raises `NotFoundError` by default. Implement
the real guard once child profiles exist.

- Create `backend/app/child_profiles/` module: `models.py` (ChildProfile ORM — FK to
  `accounts`, `display_name`, `created_at`), migration `0010_child_profiles.py`.
- Replace the stub in `backend/app/presentation/api/middleware/child_profile.py` with a
  real ownership check against the new table.
- Unit tests: administrator bypasses check; parent with matching ID passes; parent with
  non-matching ID raises `PermissionError`.

### 1.2 Background Job Retry Logic (T032–T035)

The worker processes jobs but has no retry/exponential-backoff. On failure, status stays
`running` forever.

- Alembic migration: add `'retrying'` and `'permanent_failure'` to `job_audit.status`.
- `backend/app/shared/job_queue.py` `enqueue_job()`: idempotency check.
- Extend `backend/app/worker.py`: on failure → if attempts < 3 re-enqueue with
  30s/120s/480s delay; else mark `permanent_failure`.
- Unit tests for status transitions and retry counts.

### 1.3 Health Endpoint Integration Tests (T036)

The degraded-state and DB-down HTTP 503 paths are not tested.

- `backend/tests/integration/test_health.py`: degraded when only Redis is down (200);
  unavailable when DB is down (503); `X-Request-ID` present in all responses.

### 1.4 Correlation ID Propagation (T037–T038)

Background jobs don't carry the originating `request_id` into their log entries.

- Extend `enqueue_job()` to capture `request_id_var.get()` and embed it in the job payload.
- Extend `worker.py` to call `set_request_id(job["request_id"])` before processing.
- Integration test: request with custom `X-Request-ID` → same value reflected in response
  header and error body.

### 1.5 Type / Lint Polish (T041–T044)

- Run `mypy .` in `backend/` under strict mode; fix all new errors introduced by 002–009.
- Run `ruff check . && black --check .`; fix violations.
- Confirm full test suite green (`pytest -m unit && pytest -m integration`).

---

## 2. Backend — Statistics Module (Spec not yet created)

Full spec at `docs/economy/spec-statistics.md`. No implementation exists.

### 2.1 Database Migration

New tables: `player_stats` (one row per account), `avatar_stats` (one row per avatar),
`race_sessions` (append-only history). Migration `0011_statistics.py`.

### 2.2 Domain Layer

- `backend/app/statistics/models.py` — ORM mapped classes.
- `backend/app/statistics/repository.py` — upsert `player_stats`, upsert `avatar_stats`,
  insert `race_session`.
- `backend/app/statistics/domain_service.py` — `update_on_race(account_id, race_result)`
  runs steps 1–3 from spec-statistics.md §Statistics Update Workflow in one transaction;
  `get_player_stats()`, `get_avatar_stats()`, `get_history(page)`, `get_weekly_summary()`.
- Wire into `backend/app/races/domain_service.py` `persist_race()` after XP/achievements
  (same transaction pattern as progression and achievements).

### 2.3 API Endpoints

All six endpoints from spec-statistics.md §API Endpoints under `/api/v1/players/{id}/`:
`statistics`, `avatars/{avatar_id}/statistics`, `history`, `weekly-summary`,
`personal-records`, `export` (CSV, parent auth only).

### 2.4 Tests

Unit tests for aggregation formulas (accuracy, favourite operation, streak). Integration
tests for all six endpoints including pagination, deleted-avatar edge case, training mode.

---

## 3. Frontend — Infrastructure & Design System

Nothing in `frontend/src/` is user-visible yet. These are prerequisites for all UI work.

### 3.1 Router

Install React Router and create route definitions for all 10 pages from
`docs/ui/spec-ui-implementation.md §Page Inventory`:
`/`, `/avatars`, `/avatars/new`, `/race/setup`, `/race/:id`, `/race/:id/results`,
`/statistics`, `/settings`, `/parent`, `/championship/:id`.

### 3.2 API Client

Create `frontend/src/infrastructure/api-client.ts` implementing the typed `APIClient` class
from spec-ui-implementation.md (retry on 5xx, exponential backoff, `APIError` on 4xx).
Replace direct `fetch` calls in all existing `*Api.ts` modules to use it.

### 3.3 Design Tokens

Create `frontend/src/shared/tokens.ts` with spacing, radius, animation, and colour tokens
from `docs/art/ui-style.md`. All components must use tokens — no hardcoded values.

### 3.4 Shared UI Primitives

Minimum set required by all pages:
- `Button` (primary / secondary / ghost variants)
- `Card` (avatar card, result card)
- `XPBar` (current XP progress toward next level)
- `LoadingSpinner` (with friendly message)
- `ErrorState` (child-friendly error messages from spec-ui §Child-Facing Error Messages)
- `ConfirmDialog` (focus-trapped modal, Cancel + Confirm)
- `NotificationToast` (3-second auto-dismiss, top-right)

---

## 4. Frontend — Authentication Flow

### 4.1 Login and Register Pages

Parent email/password form. On success: redirect to Child Profile Select.
On pending/rejected: show friendly message.

### 4.2 Child Profile Select Page

List child profiles for the authenticated parent. "Add Profile" button.
Selecting a profile sets the active child context (stored in session state).

### 4.3 Auth Context & Guards

React context holding `account`, `activeChild`, `login()`, `logout()`.
Route guard: unauthenticated → redirect to `/login`.
Parent-only guard: non-parent → redirect to home.

---

## 5. Frontend — Avatar Flow

### 5.1 Avatar Gallery Page (`/avatars`)

Grid of avatar cards (name, portrait thumbnail, race count). Empty state with
"Create Your First Avatar" CTA. In-progress generation shows skeleton card polling
`GET /api/v1/avatars/{id}/jobs/{job_id}` every 3 seconds. Favourite marker. Manage
button (rename, regenerate, delete).

### 5.2 Avatar Creator Page (`/avatars/new`)

Step-by-step wizard:
1. Species selection (Fox, Rabbit, Bear, Cat, Mouse)
2. Colour customisation (fur/skin hex picker, eye colour)
3. Accessories selection (checkboxes)
4. Clothing selection (sports outfit options)
5. Generation progress screen (animated placeholder, polling job status)
6. Reveal screen (portrait shown, biography displayed, name suggested, child can rename)

Uses `createAvatar()` from `engine/avatar/avatarApi.ts`.

---

## 6. Frontend — Race Flow

### 6.1 Race Setup Page (`/race/setup`)

Mode selector (Quick Race, Championship, Duel, Training). Opponent count slider (1–4).
Difficulty tier display (derived from backend). "Start Race" button. Championship
creation for Championship mode.

### 6.2 Countdown Screen

3-2-1-GO animation. Uses the race engine `COUNTDOWN` state.
Screen reader: `aria-live="polite"` counter.

### 6.3 Race Screen (`/race/:id`)

Main gameplay view wired to `useRaceEngine`:
- Horizontal scrolling race track (CSS-based, no external lib needed for v1.0)
- Runner markers (avatar portrait thumbnails at their current distance positions)
- Problem Card: large-text arithmetic problem centred on screen; `aria-label` with problem text
- Numeric answer input (auto-focused, `type="number"`)
- Per-problem timer bar (visual countdown)
- Position indicator (1st / 2nd / 3rd…)
- Progress bar (distance to finish per runner)

Wires `useRaceEngine` → renders state → calls `submitAnswer()` on input submission.
Disables browser Back during `RACING` state with a confirmation dialog.

### 6.4 Results Screen (`/race/:id/results`)

Finishing positions table (`<table>` with proper headers). XP earned breakdown.
Correct/incorrect count per participant. `AchievementToast` component (already built).
Level-up overlay when `progression.level_up` is present in the API response.
"Race Again" / "Back to Menu" buttons.

### 6.5 Championship Standings Page (`/championship/:id`)

Current standings table. "Next Race" button. Auto-transitions to ceremony view on
final race completion (`status: "completed"`).

---

## 7. Frontend — Progression & Statistics

### 7.1 Statistics Page (`/statistics`)

Player-level stats (accuracy, avg response time, favourite operation, best streak, total
races). Per-avatar stats table. Race history list (paginated, 20 per page). Uses
statistics API endpoints from section 2.3.

### 7.2 Level-Up Overlay Component

Full-screen animated overlay when `progression.level_up` fires on race results.
Shows new level, XP milestone, and a brief celebration animation.
`prefers-reduced-motion` guard.

---

## 8. Frontend — Settings & Parent Dashboard

### 8.1 Settings Page (`/settings`)

Audio volume controls (master, music, SFX, ambience, character voices) — persisted to
`localStorage`. Difficulty tier display (current adaptive tier + parent override).
Accessibility toggle for reduced motion.

### 8.2 Parent Dashboard Page (`/parent`)

Requires parent auth. Weekly summary card (problems solved, accuracy, avg time,
strongest/weakest operation — from `GET /api/v1/players/{id}/weekly-summary`).
Difficulty tier override per child (PATCH `/api/v1/players/{id}/difficulty`).
Data export button (CSV download). Delete child profile option with confirmation dialog.

---

## 9. Frontend — Audio Engine (Code Only)

The spec at `docs/engineering/audio-design.md` defines six independent audio layers.
The audio *files* are external (see the companion document), but the audio engine code
is pure TypeScript and fully buildable:

- `frontend/src/engine/audio/audioEngine.ts` — Web Audio API context, layer mixer,
  volume controls, priority system (spec §Audio Priority).
- `frontend/src/engine/audio/soundSprites.ts` — sprite map for low-latency UI sounds.
- `frontend/src/engine/audio/hooks/useAudio.ts` — React hook exposing `play()`,
  `setVolume()`, `setMuted()` per layer.
- Settings page volume sliders wire to `useAudio`.
- `AchievementToast` chime implementation (currently a stub) wired to `audioEngine`.
- Preload all race sounds before `RACING` state starts.
- All audio gracefully no-ops when `AudioContext` creation fails (spec §Edge Case 4 in
  spec-ui-implementation.md).

---

## 10. Frontend — Accessibility Hardening

Audit every built page against `docs/ui/spec-ui-implementation.md §Accessibility
Implementation Checklist`:
- Tab order in logical reading order.
- 2px focus outline, minimum 3:1 contrast.
- `alt` text or `aria-hidden` on all images.
- Text colour contrast ≥ 4.5:1.
- `prefers-reduced-motion` disables non-essential animations everywhere.
- `aria-live="polite"` on the race countdown timer.
- `aria-label` on the math problem input.
- Focus trap + Escape dismiss on all dialogs.
- Results table uses `<table>` with `scope="col"` / `scope="row"`.

---

## 11. Frontend — Offline Degradation

Implement the offline rules from spec-ui-implementation.md §Offline Degradation Rules:
- `navigator.onLine` + connection probe on app load.
- Avatar Creator: disabled when offline — show "Internet required" message.
- Race Setup: only Training Mode enabled when offline.
- Statistics: show cached data with a sync indicator.
- Parent Dashboard: disabled when offline.

---

## Priority Order

| Priority | Area | Unlocks |
|----------|------|---------|
| P0 | §3 Frontend infrastructure + auth flow | All other pages |
| P1 | §5 Avatar flow | Core child experience |
| P1 | §6 Race flow | Core gameplay |
| P2 | §7 Statistics + §8 Parent Dashboard | Parent value prop |
| P2 | §2 Statistics backend | Statistics page |
| P3 | §9 Audio engine | Immersion |
| P3 | §10–11 Accessibility + Offline | Quality gate |
| P4 | §1 Backend 002 gaps | Infrastructure completeness |
