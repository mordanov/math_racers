# Tasks: Player Achievements

**Input**: Design documents from `specs/009-achievements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create the module skeleton so all subsequent tasks have concrete file targets.

- [X] T001 Create `backend/app/achievements/__init__.py` (empty)
- [X] T002 [P] Create `backend/app/achievements/presentation/__init__.py`, `backend/app/achievements/presentation/api/__init__.py`, `backend/app/achievements/presentation/api/v1/__init__.py` (empty init files)
- [X] T003 [P] Create `backend/tests/unit/achievements/__init__.py` and `backend/tests/integration/achievements/__init__.py` (empty)
- [X] T004 [P] Create `frontend/src/engine/achievements/` and `frontend/src/components/achievements/` directories (placeholder `.gitkeep` or first real file)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Alembic migration and ORM model that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create Alembic migration `backend/alembic/versions/0009_achievements.py` — adds `player_achievements` table with columns `id` (UUID PK), `account_id` (UUID FK → `accounts.id` CASCADE), `achievement_key` (VARCHAR NOT NULL), `avatar_id` (UUID FK → `avatars.id` SET NULL, nullable), `unlocked_at` (TIMESTAMPTZ NOT NULL server default `now()`); unique constraint on `(account_id, achievement_key)`; index `idx_player_achievements_account_id` on `account_id`; include downgrade
- [X] T006 Create `backend/app/achievements/models.py` — `PlayerAchievement` SQLAlchemy ORM mapped class (`__tablename__ = "player_achievements"`) matching the migration: UUID PK `id`, UUID FK `account_id`, `achievement_key: Mapped[str]`, nullable UUID FK `avatar_id`, `unlocked_at: Mapped[datetime]`; unique constraint, index; follow exact style of `backend/app/progression/models.py`
- [X] T007 Create `backend/app/achievements/catalogue.py` — static achievement catalogue as a `@dataclass` `AchievementDef(key, category, title, description, hidden, icon_path)` and a `CATALOGUE: list[AchievementDef]` with initial entries: `first_race`, `perfect_race`, `podium_finisher`, `champion`, `level_5`, `level_10`, `level_20`; categories from spec; no hidden entries in the initial set except one example hidden achievement `hidden_speedster`

**Checkpoint**: Migration applied (`alembic upgrade head`), model importable, catalogue importable.

---

## Phase 3: User Story 1 — Earn an Achievement (Priority: P1) 🎯 MVP

**Goal**: Backend records achievement unlocks idempotently when qualifying domain events occur. The race POST response includes `new_achievements`.

**Independent Test**: POST `/api/v1/races` for a new player → response contains `new_achievements: [{key: "first_race", ...}]`; second identical POST (same `race_id`) returns 409 with no duplicate records; `GET /api/v1/players/{id}/achievements` shows exactly one `first_race` entry.

### Implementation for User Story 1

- [X] T008 [US1] Create `backend/app/achievements/schemas.py` — Pydantic schemas: `AchievementResponse(key, category, title, description, hidden, icon_path, unlocked_at: datetime | None)` and `PlayerAchievementResponse` (extends with `avatar_id: uuid.UUID | None`); follow style of `backend/app/progression/schemas.py`
- [X] T009 [US1] Create `backend/app/achievements/repository.py` — `AchievementRepository` Protocol with `async def get_unlocked(account_id) -> list[PlayerAchievement]` and `async def unlock(account_id, achievement_key, avatar_id=None) -> PlayerAchievement | None` (returns None if already unlocked); `SQLAlchemyAchievementRepository` implementation using `INSERT INTO player_achievements ... ON CONFLICT (account_id, achievement_key) DO NOTHING RETURNING *` via `text()` or ORM upsert; follow style of `backend/app/progression/repository.py`
- [X] T010 [US1] Create `backend/app/achievements/domain_service.py` — `AchievementDomainService(repository: AchievementRepository)` with: `async def evaluate_race_completed(account_id, race_result, session) -> list[AchievementResponse]` that evaluates predicates for `RaceCompletedEvent` triggers (`first_race`, `perfect_race`, `podium_finisher`, `champion`) catching per-predicate exceptions; `async def evaluate_level_up(account_id, new_level, session) -> list[AchievementResponse]` for `level_5`, `level_10`, `level_20`; predicate registry dict keyed by achievement key; predicates are async pure functions `(account_id, event_data, session) -> bool`
- [X] T011 [US1] Add `new_achievements: list[AchievementResponse]` field (default `[]`) to `RaceSummaryResponse` in `backend/app/races/schemas.py`
- [X] T012 [US1] Update `backend/app/races/domain_service.py` `persist_race()` to instantiate `AchievementDomainService` and call `evaluate_race_completed()` after XP is awarded; if `level_up` event was returned by progression, also call `evaluate_level_up()`; populate `response.new_achievements`; accept `AchievementRepository | None` as optional constructor param (same pattern as `progression_repository`)
- [X] T013 [US1] Update `backend/app/races/presentation/api/v1/races.py` `create_race()` to instantiate `SQLAlchemyAchievementRepository(session)` and pass it to `RaceDomainService`
- [X] T014 [US1] Write unit tests `backend/tests/unit/achievements/test_domain_service.py` covering: `first_race` predicate fires for a new player; `perfect_race` fires only with 8/8 correct; `level_5` fires at level 5 but not 4; already-unlocked achievement is skipped (idempotency); predicate exception is caught and does not abort other evaluations
- [X] T015 [US1] Write integration tests `backend/tests/integration/achievements/test_api_achievements.py` — Scenario 1 (first race unlocks `first_race`, appears in response); Scenario 2 (duplicate race POST 409, no duplicate achievement); Scenario 4 (8/8 correct unlocks both `first_race` and `perfect_race`)

**Checkpoint**: All unit and integration tests for US1 pass. `pytest -m unit` and `pytest -m integration` green.

---

## Phase 4: User Story 2 — Browse Achievements (Priority: P2)

**Goal**: `GET /api/v1/achievements` returns catalogue (hidden items excluded); `GET /api/v1/players/{id}/achievements` returns unlock list with timestamps.

**Independent Test**: GET `/api/v1/achievements` → hidden entries absent; GET `/api/v1/achievements?account_id={id}` after unlocking a hidden achievement → hidden entry now present; GET `/api/v1/players/{id}/achievements` → full unlock list with `unlocked_at`; GET with wrong account → 403.

### Implementation for User Story 2

- [X] T016 [US2] Create `backend/app/achievements/presentation/api/v1/achievements.py` — FastAPI router with: `GET /api/v1/achievements` (optional `account_id` query param, no auth required; filters hidden entries using `AchievementDomainService.get_visible_catalogue(account_id)`); `GET /api/v1/players/{account_id}/achievements` (requires auth via `get_current_account`; returns 403 if `account.id != account_id` and not admin; returns full unlock list); follow style of `backend/app/progression/presentation/api/v1/progression.py`
- [X] T017 [US2] Add `async def get_visible_catalogue(account_id: uuid.UUID | None, session) -> list[AchievementResponse]` to `AchievementDomainService` in `backend/app/achievements/domain_service.py` — returns all non-hidden catalogue entries plus any hidden entries already unlocked by `account_id`; `unlocked_at` field populated from unlock records
- [X] T018 [US2] Register achievements router in `backend/app/main.py` — import and `app.include_router(achievements_router)` following the pattern of other routers
- [X] T019 [US2] Add integration tests to `backend/tests/integration/achievements/test_api_achievements.py` — Scenario 3 (hidden achievement absent from catalogue for non-owner, present for owner); Scenario 6 (403 when requesting another player's achievement list)
- [X] T020 [US2] Create `frontend/src/engine/achievements/types.ts` — TypeScript interfaces: `Achievement { key, category, title, description, hidden, icon_path, unlocked_at: string | null }` and `PlayerAchievement` (extends with `avatar_id: string | null`)
- [X] T021 [US2] [P] Create `frontend/src/engine/achievements/achievementsApi.ts` — `fetchAchievements(accountId?: string): Promise<Achievement[]>` and `fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]>` using `fetch` with `credentials: 'include'`

**Checkpoint**: Both endpoints return correct data; hidden filtering verified; 403 on cross-account access.

---

## Phase 5: User Story 3 — Achievement Celebration (Priority: P3)

**Goal**: Frontend displays sequential badge animation on the Results Screen only; deferred from active race; respects `prefers-reduced-motion`.

**Independent Test**: After a race that yields `new_achievements` in the POST response, Results Screen shows badge animation within 2 seconds; two achievements queue sequentially with 2-second gap; animation does not appear during `RACING` state; with `prefers-reduced-motion: reduce`, badge appears immediately without animation.

### Implementation for User Story 3

- [X] T022 [US3] Update `frontend/src/engine/race/raceApi.ts` `postRaceSummary()` to return `{ new_achievements: Achievement[] }` from the 201 response body (parse JSON before returning); update `RaceSummary` return type
- [X] T023 [US3] Create `frontend/src/components/achievements/AchievementToast.tsx` — React component that accepts `achievements: Achievement[]` prop; renders nothing unless `raceState === 'RESULTS'`; drains queue one at a time: sparkle particle effect (CSS animation, 0.3s), badge scale-in with bounce easing (CSS animation, 0.5s), chime sound via Web Audio API (short ascending notes), fanfare (0.4s); total ≤ 2 seconds per achievement; 2-second gap between items; all animations wrapped in `useReducedMotion()` check — if reduced motion, render badge immediately without animation; accessible: `role="status"`, `aria-live="polite"`
- [X] T024 [US3] Write vitest unit tests `frontend/src/components/achievements/AchievementToast.test.tsx` — renders nothing in `RACING` state; renders badge in `RESULTS` state; queues two achievements sequentially (timer-based test); with `prefers-reduced-motion` set, no animation class applied

**Checkpoint**: `AchievementToast` renders correctly in Results state, skips animation with reduced-motion, queues multiple achievements.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T025 Write unit tests `backend/tests/unit/achievements/test_catalogue.py` — no duplicate keys; all required fields present; all `category` values in the allowed set; icon paths have expected format
- [X] T026 [P] Add `longest_streak` to `frontend/src/engine/race/types.ts` `ParticipantSummary` interface (required by spec 008; used to pass correct data in race POST body)
- [X] T027 Run `scripts/run-local-ci-checks.sh` from repo root; fix any format/lint/type/test failures introduced by this feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 2; US1 must be complete for the integration test in Scenario 4 to be reusable, but US2 is independently testable
- **Phase 5 (US3)**: Depends on US1 (needs `new_achievements` field in race response)
- **Phase 6 (Polish)**: Depends on all user stories complete

### Within Each User Story

- T008 (schemas) before T009 (repository) before T010 (domain service)
- T011 (extend RaceSummaryResponse) before T012 (update domain service)
- T012 before T013 (update router)
- T016 (router) depends on T017 (domain service method)
- T022 (raceApi) before T023 (AchievementToast)

### Parallel Opportunities

- T001–T004 (Phase 1): all parallel
- T005 (migration) and T007 (catalogue) can run in parallel with T006 (model)
- T008 and T020/T021 (frontend types/api) can run in parallel after Phase 2
- T016 and T020/T021 can run in parallel (different files)

---

## Parallel Example: Phase 2

```
Task A: T005 — Write Alembic migration 0009_achievements.py
Task B: T006 — Write PlayerAchievement ORM model
Task C: T007 — Write catalogue.py with AchievementDef dataclass
```

## Parallel Example: US1 + US2 frontend

```
Task A: T020 — types.ts
Task B: T021 — achievementsApi.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (migration + model + catalogue)
3. Complete Phase 3: US1 (domain service + race integration + tests)
4. **STOP and VALIDATE**: `pytest -m unit` and `pytest -m integration` pass; POST race returns `new_achievements`
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → achievements earned on race completion (backend only)
3. US2 → catalogue and unlock list browsable (backend + minimal frontend fetch)
4. US3 → celebration animation on Results Screen (frontend polish)
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story
- Catalogue is a static Python module — no DB seed step required
- The `ON CONFLICT DO NOTHING` upsert pattern is the idempotency guarantee
- `avatar_id` column is nullable and present from day one to avoid a future migration
- Achievement evaluation is called synchronously within the existing `persist_race` transaction
