# Tasks: AI Opponents

**Input**: Design documents from `specs/005-ai-opponents/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Skeleton Modules)

**Purpose**: Create new directories and empty `__init__.py` files so subsequent tasks can import from them.

- [x] T001 Create backend/app/opponents/__init__.py, backend/tests/unit/opponents/__init__.py, and backend/tests/integration/opponents/__init__.py as empty files

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Extend the shared `AiPersonality` type — all simulation and personality code depends on this shape.

**⚠️ CRITICAL**: No US1, US2, or US3 frontend work can begin until this is complete.

- [x] T002 Extend `AiPersonality` interface in `frontend/src/engine/race/types.ts` — add three fields: `name: string`, `speedProfile: 'uniform' | 'front_loaded' | 'back_loaded' | 'random'`, `tierOffset: number`; keep existing fields (`id`, `accuracyRate`, `baseResponseTimeMs`, `responseTimeVarianceMs`) unchanged for backward compatibility

**Checkpoint**: Extended type in place — US1, US2, US3 frontend tasks can now begin.

---

## Phase 3: User Story 1 — Race Against AI Opponents (Priority: P1) 🎯 MVP

**Goal**: Checkpoint-aware simulation runs correctly for any personality, with per-opponent RNG independence, zero movement on incorrect answers, and deterministic tiebreaking.

**Independent Test**: Run `pnpm vitest run tests/engine/race/aiRunner.test.ts tests/engine/race/raceEngine.integration.test.ts` — all added tests pass.

### Implementation

- [x] T003 [US1] Update `simulateAiObstacle` in `frontend/src/engine/race/aiRunner.ts` — add `checkpointIndex: number` as second parameter (before `rng`); replace the Gaussian noise response-time model with `sampleResponseTime` + `speedMultiplier` per `contracts/ai-simulation.md`; preserve the `accuracyRoll` logic; return type `AiObstacleResult` unchanged

- [x] T004 [US1] Update `createRaceEngine` in `frontend/src/engine/race/raceEngine.ts` — (1) replace single `aiRng = createRng(config.seed + 1)` with per-participant array `aiRngs` using `createRng(config.seed + i + 1)` where `i` is the 0-based participant index; (2) pass the per-opponent `rng` and `obstacleIndex` to `simulateAiObstacle`; (3) fix `getSummary` tiebreaker from `runners.indexOf(a) - runners.indexOf(b)` to `a.runnerId < b.runnerId ? -1 : 1`

### Tests

- [x] T005 [P] [US1] Extend `frontend/tests/engine/race/aiRunner.test.ts` — add tests: (a) same seed + same checkpointIndex produces identical result (determinism per checkpoint); (b) Speedster at checkpointIndex=0 vs checkpointIndex=7 produces lower responseTimeMs at index 0 (front_loaded arc); (c) Slow Starter at checkpointIndex=7 produces lower responseTimeMs than at checkpointIndex=0 (back_loaded arc); (d) `accuracyRate=0.0` always returns `isCorrect=false` regardless of checkpointIndex (existing test extended to cover new signature)

- [x] T006 [P] [US1] Extend `frontend/tests/engine/race/raceEngine.integration.test.ts` — add tests: (a) race with 3 AI opponents of the same personality produces at least one checkpoint where not all 3 distances are identical (per-opponent RNG independence); (b) race with zero AI opponents completes and `getSummary()` returns 1 participant; (c) two replays of the same race (same seed, same personalities) produce identical `totalDistanceMetres` per AI runner; (d) `getSummary()` tiebreaker is stable — same tied race replayed twice returns the same runner at position 1

**Checkpoint**: US1 complete and testable. `pnpm vitest run` passes.

---

## Phase 4: User Story 2 — Distinct Personality Behaviours (Priority: P2)

**Goal**: Five named AiPersonality constants exist and produce visibly distinct checkpoint-by-checkpoint patterns when used with the updated `simulateAiObstacle`.

**Independent Test**: Run `pnpm vitest run tests/engine/race/personalities.test.ts` — all tests pass.

### Implementation

- [x] T007 [US2] Create `frontend/src/engine/race/personalities.ts` — export five named `AiPersonality` constants (`STEADY`, `SPEEDSTER`, `SLOW_STARTER`, `UNPREDICTABLE`, `BALANCED`) using the exact field values from `data-model.md` constants table; also export a `PERSONALITIES` array containing all five; no fetch logic in this task

### Tests

- [x] T008 [US2] Create `frontend/tests/engine/race/personalities.test.ts` — tests: (a) `PERSONALITIES.length === 5`; (b) each personality has a unique `id` and a non-empty `name`; (c) `SPEEDSTER.speedProfile === 'front_loaded'`, `SLOW_STARTER.speedProfile === 'back_loaded'`, `UNPREDICTABLE.speedProfile === 'random'`, `STEADY.speedProfile === 'uniform'`; (d) using `simulateAiObstacle` + `createRng`, Speedster's average `responseTimeMs` at checkpoints 0–2 is lower than at checkpoints 5–7 over 20 seeds; (e) Slow Starter's average `responseTimeMs` at checkpoints 5–7 is lower than at checkpoints 0–2 over 20 seeds

**Checkpoint**: US2 complete. All 5 personalities defined and verified distinct.

---

## Phase 5: User Story 3 — Personality Configuration Endpoint (Priority: P3)

**Goal**: `GET /api/v1/opponents/personalities` returns 5 personality definitions without authentication; frontend has a `fetchPersonalities()` function that calls it.

**Independent Test**: `pytest -m unit tests/unit/opponents/` passes; `pytest -m integration tests/integration/opponents/` passes (with stack running).

### Implementation

- [x] T009 [P] [US3] Create `backend/app/opponents/schemas.py` — define `PersonalityDefinitionResponse` Pydantic model with fields matching `contracts/get-personalities.md` (`id`, `name`, `accuracy_rate → accuracyRate`, `base_response_time_ms → baseResponseTimeMs`, `response_time_variance_ms → responseTimeVarianceMs`, `speed_profile → speedProfile`, `tier_offset → tierOffset`); use `model_config = ConfigDict(populate_by_name=True)` and `Field(alias=...)` for camelCase serialisation

- [x] T010 [P] [US3] Create `backend/app/opponents/personalities.py` — define `PERSONALITIES: list[PersonalityDefinitionResponse]` with the 5 hardcoded entries from `data-model.md` constants table; import schema from `app.opponents.schemas`

- [x] T011 [US3] Create `backend/app/presentation/api/v1/opponents.py` — define `router = APIRouter(prefix="/api/v1", tags=["opponents"])` with a single `GET /opponents/personalities` route that returns `PERSONALITIES`; `response_model=list[PersonalityDefinitionResponse]`; no authentication dependency

- [x] T012 [US3] Register the opponents router in `backend/app/main.py` — add `from app.presentation.api.v1.opponents import router as opponents_router` and `app.include_router(opponents_router)` in `create_app()`, following the same pattern as `problems_router` and `difficulty_router`

- [x] T013 [P] [US3] Add `fetchPersonalities()` to `frontend/src/engine/race/personalities.ts` — async function that calls `GET /api/v1/opponents/personalities` (use the same base URL pattern as `raceApi.ts`) and returns `AiPersonality[]`; map response JSON fields from camelCase to the `AiPersonality` interface fields

### Tests

- [x] T014 [P] [US3] Create `backend/tests/unit/opponents/test_personalities.py` — unit tests (no DB, no HTTP): (a) `len(PERSONALITIES) == 5`; (b) all `id` values are unique; (c) all `accuracy_rate` values are in `[0.0, 1.0]`; (d) all `speed_profile` values are one of `{"uniform", "front_loaded", "back_loaded", "random"}`; (e) `SPEEDSTER.tier_offset == 1`; (f) schema serialises with camelCase aliases (`accuracyRate` present, `accuracy_rate` absent in `.model_dump(by_alias=True)`)

- [x] T015 [US3] Create `backend/tests/integration/opponents/test_api_opponents.py` — integration tests: (a) `GET /api/v1/opponents/personalities` returns `200` without `Authorization` header; (b) response is a JSON array of length 5; (c) each item has `id`, `name`, `accuracyRate`, `baseResponseTimeMs`, `responseTimeVarianceMs`, `speedProfile`, `tierOffset`; (d) `speedProfile` values are all in the valid enum set

**Checkpoint**: US3 complete. Backend endpoint live; frontend fetch function ready.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full suite passes end-to-end and confirm type safety.

- [x] T016 Run `pnpm tsc --noEmit` in `frontend/` and fix any TypeScript errors from the updated `AiPersonality` interface or `simulateAiObstacle` signature; run `pnpm vitest run` to confirm all frontend tests pass; run `pytest -m unit` in `backend/` to confirm all backend unit tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1
- **Phase 3 (US1)**: Depends on Phase 2 — T003 and T004 must run sequentially (T003 before T004); T005 and T006 depend on T004 but are parallel with each other
- **Phase 4 (US2)**: Depends on Phase 2 (T002) — T007 can run in parallel with Phase 3 tasks since it is a different file; T008 depends on T007 and T003 (uses simulateAiObstacle)
- **Phase 5 (US3)**: T009 and T010 can run in parallel with Phase 3/4 (different files); T011 depends on T009+T010; T012 depends on T011; T013 depends on T002; T014 depends on T010; T015 depends on T012
- **Phase 6 (Polish)**: Depends on all phases complete

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (T002)
- **US2 (P2)**: Depends on Foundational (T002) and US1 simulation logic (T003 for meaningful behaviour tests)
- **US3 (P3)**: Backend tasks (T009–T012, T014–T015) are independent of US1/US2; T013 (frontend fetch) depends on T002 only

### Parallel Opportunities Within US3

```
T009 (schemas.py) ─┐
                    ├─→ T011 (router) → T012 (register in main.py) → T015 (integration test)
T010 (personalities.py) ─┘
         │
         └─→ T014 (unit test)  [parallel with T011]

T013 (fetchPersonalities frontend) — parallel with all backend US3 tasks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup (T001)
2. Phase 2: Foundational (T002)
3. Phase 3: US1 — T003 → T004 → T005 + T006 (parallel)
4. **STOP and VALIDATE**: `pnpm vitest run` passes
5. Demo: race engine now uses checkpoint-aware AI with per-opponent RNG

### Incremental Delivery

1. Setup + Foundational → Phase 2 complete
2. US1 → checkpoint-aware simulation with determinism guarantees (**MVP**)
3. US2 → named personality constants with verified distinct behaviour arcs
4. US3 → backend endpoint + frontend fetch function
5. Polish → full suite green

### Parallel Opportunities Summary

- T005 and T006 (US1 tests) — parallel with each other
- T009 and T010 (US3 backend schemas + constants) — parallel with each other AND with Phase 3/4 tasks
- T013 (US3 frontend fetch) — parallel with T009–T012 backend tasks
- T014 (US3 unit test) — parallel with T011/T012

---

## Notes

- `simulateAiObstacle` call-site is only in `raceEngine.ts` — one place to update for the signature change
- Existing `aiRunner.test.ts` constructs `AiPersonality` inline without `speedProfile`/`tierOffset` — those tests will need the two new fields added to inline fixtures (T005 covers this)
- The `MEDIUM` fixture in the existing test must gain `speedProfile: 'uniform'` and `tierOffset: 0` after T002 to keep TypeScript happy
- `fetchPersonalities()` calls no endpoint during vitest unit tests — unit tests import constants from `personalities.ts` directly; only integration tests (T015) call the live server
