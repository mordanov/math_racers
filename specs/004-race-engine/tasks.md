# Tasks: Race Engine

**Input**: Design documents from `specs/004-race-engine/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Tests**: Included — the spec's Definition of Done and FR coverage require automated tests.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the directory skeletons and shared constants that all subsequent tasks depend on.

- [ ] T001 Create `frontend/src/engine/race/` directory structure: `index.ts`, `types.ts`, `constants.ts`, `stateMachine.ts`, `movement.ts`, `clock.ts`, `aiRunner.ts`, `raceEngine.ts`, and `hooks/useRaceEngine.ts` (empty stubs only)
- [ ] T002 Create `frontend/tests/engine/race/` directory with placeholder `__init__` markers so Vitest discovers the suite
- [ ] T003 Create `backend/app/races/` bounded-context directory with `__init__.py`, `models.py`, `schemas.py`, `repository.py`, `domain_service.py` (empty stubs only)
- [ ] T004 [P] Create `backend/tests/unit/races/` and `backend/tests/integration/races/` directories with `__init__.py` stubs

**Checkpoint**: Directory structure matches plan.md — all empty stubs in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared types, constants, and database migration that every user story builds on.

- [ ] T005 Define all TypeScript types in `frontend/src/engine/race/types.ts`: `RaceState`, `RaceMode`, `MovementTier`, `TierResult`, `ObstacleResult`, `RunnerState`, `AiPersonality`, `RaceConfig`, `ParticipantConfig`, `RaceEngineState`, `RaceSummary`, `ParticipantSummary` — exactly as specified in `data-model.md`
- [ ] T006 Define all named constants in `frontend/src/engine/race/constants.ts`: `OBSTACLE_COUNT = 8`, `MAX_TRACK_DISTANCE = 144`, `PERFECT_THRESHOLD_MS = 2000`, `EXCELLENT_THRESHOLD_MS = 4000`, `GOOD_THRESHOLD_MS = 6000`, `FRAME_DELTA_CAP_MS = 100`
- [ ] T007 Write Alembic migration in `backend/alembic/versions/<timestamp>_add_races_tables.py` creating `races` and `race_participants` tables per `data-model.md` (columns, constraints, FK, audit timestamps)
- [ ] T008 [P] Define `RaceSummaryRequest` and `RaceSummaryResponse` Pydantic schemas in `backend/app/races/schemas.py` matching the contract in `contracts/race-summary-api.md`
- [ ] T009 [P] Define `Race` and `RaceParticipant` SQLAlchemy models in `backend/app/races/models.py` matching the `races` and `race_participants` table spec in `data-model.md`

**Checkpoint**: Types compile, constants are importable, migration runs cleanly — US phases can begin.

---

## Phase 3: User Story 1 — Complete a Quick Race (Priority: P1) 🎯 MVP

**Goal**: Player can start a Quick Race, progress through 8 obstacles with correct movement tier application, and reach the Results screen.

**Independent Test**: Start a Quick Race; answer all 8 questions; confirm movement matches the correct tier for each response time; confirm Results screen shows final positions.

### Implementation

- [ ] T010 [US1] Implement `calculateMovement(isCorrect, responseTimeMs)` in `frontend/src/engine/race/movement.ts` — pure function returning `TierResult`; uses constants from T006; returns `{ tier: 'incorrect', distanceMetres: 0 }` for wrong answers
- [ ] T011 [P] [US1] Implement unit tests for `calculateMovement` covering all 5 tier branches (including boundary values at 2000, 4000, 6000 ms and incorrect=false) in `frontend/tests/engine/race/movement.test.ts`
- [ ] T012 [US1] Implement the state machine in `frontend/src/engine/race/stateMachine.ts`: define `LEGAL_TRANSITIONS` record, implement `transition(from, to)` that throws `RaceStateError` on illegal transitions; export `RaceStateError`
- [ ] T013 [P] [US1] Implement unit tests for all legal and illegal transitions in `frontend/tests/engine/race/stateMachine.test.ts` (6 legal paths + at least 3 illegal paths from spec edge cases)
- [ ] T014 [US1] Implement `GameClock` class in `frontend/src/engine/race/clock.ts`: `tick(timestamp)` accumulates delta clamped to `FRAME_DELTA_CAP_MS`; `pause()`, `resume()`, `reset()`, `getMs()` methods; no side effects outside class
- [ ] T015 [P] [US1] Implement unit tests for `GameClock` in `frontend/tests/engine/race/clock.test.ts`: verify accumulation, delta clamping, pause/resume correctness (paused duration not counted), and reset
- [ ] T016 [US1] Implement `createRaceEngine(config)` factory in `frontend/src/engine/race/raceEngine.ts` wiring `stateMachine`, `GameClock`, and `calculateMovement`; implement `transition()`, `tick(timestamp)`, `submitAnswer({ isCorrect })`, `getState()`, `getSummary()` (throws if not in RESULTS)
- [ ] T017 [US1] Implement `useRaceEngine(config)` hook in `frontend/src/engine/race/hooks/useRaceEngine.ts`: wraps `createRaceEngine` in `useRef`; drives `engine.tick()` via `requestAnimationFrame`; registers/deregisters `visibilitychange` for clock pause/resume; exposes derived React state
- [ ] T018 [US1] Wire public exports in `frontend/src/engine/race/index.ts`: re-export `createRaceEngine`, `useRaceEngine`, all types from `types.ts`, `RaceStateError`
- [ ] T019 [US1] Implement integration test for a full 8-obstacle Quick Race (human only, no AI) in `frontend/tests/engine/race/raceEngine.integration.test.ts`: verify state sequence, movement accumulation per tier, and `getSummary()` output after RESULTS

**Checkpoint**: `pnpm test src/engine/race` passes; `calculateMovement`, state machine, clock, and engine all covered; a full race loop completes correctly in the integration test.

---

## Phase 4: User Story 2 — Race Against AI Runners (Priority: P2)

**Goal**: AI runners simulate responses using a seeded Gaussian model; same seed produces identical results; AI updates are sequential.

**Independent Test**: Run a race with 4 AI runners; confirm they move after each obstacle; replay the same seed twice and confirm identical distances.

### Implementation

- [ ] T020 [US2] Implement `gaussianNoise(rng)` (Box-Muller) and `simulateAiObstacle(personality, tier, rng)` in `frontend/src/engine/race/aiRunner.ts`; `simulateAiObstacle` returns `{ isCorrect, responseTimeMs }` with response time clipped to `[0, ∞)` and `isCorrect` drawn as Bernoulli with `personality.accuracyRate`
- [ ] T021 [P] [US2] Implement unit tests for `simulateAiObstacle` in `frontend/tests/engine/race/aiRunner.test.ts`: same seed + personality produces identical results across 10 calls; non-negative response times; `accuracyRate=1.0` always returns `isCorrect=true`; `accuracyRate=0.0` always returns `isCorrect=false`
- [ ] T022 [US2] Extend `createRaceEngine` in `frontend/src/engine/race/raceEngine.ts` to initialise two independent RNG instances from `config.seed` and `config.seed + 1`; after player submits each obstacle, iterate AI runners sequentially (one per tick) calling `simulateAiObstacle` then `calculateMovement`; update `RunnerState` accordingly
- [ ] T023 [US2] Extend integration test in `frontend/tests/engine/race/raceEngine.integration.test.ts` with a determinism test: run a 4-AI race twice with the same seed and assert all `RunnerState` outcomes are identical

**Checkpoint**: AI runners move each obstacle; determinism test passes; sequential update order verified.

---

## Phase 5: User Story 3 — Race State Machine Enforcement (Priority: P2)

**Goal**: All illegal transitions are rejected; engine never enters an undefined state.

**Independent Test**: Call `engine.transition()` with every illegal pair from the spec; confirm `RaceStateError` is thrown and state is unchanged.

### Implementation

- [ ] T024 [US3] Extend unit tests in `frontend/tests/engine/race/stateMachine.test.ts` to cover all spec-listed illegal transitions: IDLE→RACING, RESULTS→RACING, COUNTDOWN→IDLE — assert `RaceStateError` is thrown and current state is unmodified after the attempt
- [ ] T025 [US3] Extend integration test in `frontend/tests/engine/race/raceEngine.integration.test.ts` with a state-guard test: attempt each illegal transition on a live engine instance; assert engine `state` field is unchanged; assert calling `submitAnswer` before RACING throws

**Checkpoint**: Zero undefined-state transitions possible; all error paths exercised.

---

## Phase 6: User Story 4 — Game Clock Accuracy (Priority: P3)

**Goal**: Per-obstacle timing correctly drives movement tier; clock pauses on tab-hide and resumes on tab-show; no timing error beyond ±50 ms.

**Independent Test**: Record time between problem visibility and submission; confirm correct tier is applied; simulate visibility change and confirm hidden duration is excluded.

### Implementation

- [ ] T026 [US4] Extend `GameClock` in `frontend/src/engine/race/clock.ts` to expose `startObstacleClock()` and `getObstacleMs()` for per-obstacle timing (called by `raceEngine.ts` when each new problem becomes visible)
- [ ] T027 [US4] Extend clock unit tests in `frontend/tests/engine/race/clock.test.ts`: simulate a visibility change mid-obstacle (pause → resume) and assert the returned `getObstacleMs()` excludes the hidden duration; verify two independent timers (game clock vs obstacle clock) advance independently
- [ ] T028 [US4] Update `raceEngine.ts` `submitAnswer()` to read `obstacleClockMs` from `GameClock.getObstacleMs()` (not from an external argument) so timing is always sourced from the engine clock

**Checkpoint**: Tier assignment is driven entirely by the engine clock; visibility-change test passes.

---

## Phase 7: User Story 5 — Race Summary Persisted (Priority: P3)

**Goal**: A complete `RaceSummary` is assembled after each race and successfully POST-ed to `/api/v1/races/`; backend validates and persists it; duplicate `race_id` returns 409.

**Independent Test**: Complete a race; inspect the persisted record; all fields match observed in-race values; attempt a second POST with the same `race_id` and confirm 409.

### Backend Implementation

- [ ] T029 [US5] Implement `RaceRepository` in `backend/app/races/repository.py`: async `create(summary)` method using SQLAlchemy; raises `RaceAlreadyExistsError` (defined in `backend/app/races/domain_service.py`) when `race_id` already exists
- [ ] T030 [P] [US5] Implement `RaceDomainService` in `backend/app/races/domain_service.py`: `persist_race(summary)` validates that positions are unique within the request (1–5, no duplicates), then delegates to `RaceRepository.create()`; raises `ValidationError` on invalid positions
- [ ] T031 [US5] Implement POST `/api/v1/races/` endpoint in `backend/app/races/presentation/api/v1/races.py`: receives `RaceSummaryRequest`, calls `RaceDomainService.persist_race()`, returns 201 `RaceSummaryResponse` on success; maps `RaceAlreadyExistsError` → 409, Pydantic `ValidationError` → 400
- [ ] T032 [US5] Register the `races` router in `backend/app/main.py` under `/api/v1/`
- [ ] T033 [P] [US5] Implement unit tests for `RaceDomainService` in `backend/tests/unit/races/test_domain_service.py`: valid summary persists; duplicate `race_id` raises `RaceAlreadyExistsError`; non-unique positions raise `ValidationError`; `problems_correct > 8` raises `ValidationError`
- [ ] T034 [P] [US5] Implement API integration tests for `POST /api/v1/races/` in `backend/tests/integration/races/test_api_races.py`: 201 on valid payload; 409 on duplicate `race_id`; 400 on invalid `difficulty_tier`; 401 on missing JWT

### Frontend Integration

- [ ] T035 [US5] Implement `postRaceSummary(summary: RaceSummary)` in `frontend/src/engine/race/raceApi.ts`: POSTs to `/api/v1/races/`; retries once on network error; does not retry on 409 (logs and swallows)
- [ ] T036 [US5] Extend `useRaceEngine` hook in `frontend/src/engine/race/hooks/useRaceEngine.ts` to call `postRaceSummary` automatically when state transitions to RESULTS; expose `summaryStatus: 'idle' | 'pending' | 'saved' | 'error'` to consuming components

**Checkpoint**: `backend/tests/integration/races/test_api_races.py` passes; completing a race in the running frontend app triggers a successful 201 to the backend; 409 handled gracefully.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, documentation sync, final validation.

- [ ] T037 [P] Update `docs/gameplay/spec-race-engine.md` with any implementation notes that deviate from or clarify the spec (per Constitution § XX — docs updated when public behaviour changes)
- [ ] T038 [P] Verify `frontend/src/engine/race/index.ts` exports are tree-shakeable (no side-effect imports); run `pnpm typecheck` with zero errors
- [ ] T039 [P] Run `pnpm lint && pnpm fmt:check` and fix any violations in new frontend files
- [ ] T040 [P] Run `ruff check backend/app/races/ && mypy backend/app/races/` and fix any violations
- [ ] T041 Follow manual verification steps from `docs/gameplay/spec-race-engine.md` §Manual Verification Steps (7 steps) and confirm all pass against the running app

**Checkpoint**: `pnpm test`, `pnpm typecheck`, `pnpm lint` all green; backend `pytest` green; manual verification checklist complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **blocks all user story phases**
- **Phase 3 (US1)**: Depends on Phase 2 — core race loop (MVP)
- **Phase 4 (US2)**: Depends on Phase 2 + T016 (engine factory must exist before AI extension)
- **Phase 5 (US3)**: Depends on T012 (state machine) — can run alongside Phase 4
- **Phase 6 (US4)**: Depends on T014, T016 (clock + engine) — can run alongside Phase 4/5
- **Phase 7 (US5)**: Depends on T016 (engine `getSummary()`); backend tasks T029–T034 are independent of frontend
- **Phase 8 (Polish)**: Depends on all prior phases complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no story dependencies
- **US2 (P2)**: Can start after Phase 2; requires T016 (engine factory)
- **US3 (P2)**: Can start after T012 (state machine) — independent of US2
- **US4 (P3)**: Can start after T014 + T016 — independent of US2/US3
- **US5 (P3)**: Backend half independent of all frontend work; frontend half requires T016 + T017

### Within Each Phase

- Models/types before services
- Services before endpoints
- Core implementation before test extension
- Commit after each logical task group

### Parallel Opportunities

- T008 and T009 (schemas and models) can run in parallel after T007
- T011, T013, T015 (tests) can run in parallel with their sibling implementation tasks
- T020 + T021 (AI runner + tests) run in parallel
- T029 + T030 (repository + domain service) run in parallel after T009
- T033 + T034 (backend unit + integration tests) run in parallel
- T037–T041 (polish) all run in parallel

---

## Parallel Example: User Story 1

```bash
# After Phase 2 completes:

# Parallel group A — movement
Task T010: Implement calculateMovement in frontend/src/engine/race/movement.ts
Task T011: Write movement unit tests in frontend/tests/engine/race/movement.test.ts

# Parallel group B — state machine
Task T012: Implement state machine in frontend/src/engine/race/stateMachine.ts
Task T013: Write state machine tests in frontend/tests/engine/race/stateMachine.test.ts

# Parallel group C — clock (independent file)
Task T014: Implement GameClock in frontend/src/engine/race/clock.ts
Task T015: Write clock tests in frontend/tests/engine/race/clock.test.ts

# Then sequentially (depends on A + B + C):
Task T016: Implement createRaceEngine in frontend/src/engine/race/raceEngine.ts
Task T017: Implement useRaceEngine hook
Task T018: Wire index.ts exports
Task T019: Full integration test
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (T010–T019)
4. **STOP and VALIDATE**: `pnpm test src/engine/race` green; full race loop runs end-to-end
5. Demo: working Quick Race with human player, correct movement tiers, Results screen

### Incremental Delivery

1. Setup + Foundational → types and constants compile, migration runs
2. Add US1 → human player race loop works (MVP)
3. Add US2 → AI runners added, determinism verified
4. Add US3 → illegal transitions blocked (could run alongside US2)
5. Add US4 → clock accuracy verified
6. Add US5 → backend persists summary; full round-trip working
7. Polish → all checks green

### Parallel Team Strategy

With two developers after Phase 2:

- **Developer A**: US1 (T010–T019) → then US4 (T026–T028)
- **Developer B**: US2 (T020–T023) → then backend half of US5 (T029–T034)
- US3 (T024–T025) can be slotted in by whichever developer finishes first

---

## Notes

- [P] tasks operate on different files with no dependencies on in-progress work
- [Story] labels map directly to user stories in `spec.md`
- Each phase is independently completable and testable
- No test task should be marked done until it fails first, then passes after implementation
- Commit after each task group or checkpoint
- `specs/004-race-engine/quickstart.md` contains the manual end-to-end walkthrough for T041
