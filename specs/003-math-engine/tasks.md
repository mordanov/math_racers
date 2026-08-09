# Tasks: Mathematics Engine

**Input**: Design documents from `specs/003-math-engine/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/math-api.md ✅, quickstart.md ✅

**Organization**: Grouped by user story for independent implementation and testing.  
**Tests**: Included — required by Constitution §XVIII and the Definition of Done.

## Format: `[ID] [P?] [Story?] Description — file path`

- **[P]**: Parallelizable (different files, no incomplete dependencies)
- **[Story]**: User story label (US1–US5); omitted for Setup/Foundational/Polish phases

---

## Phase 1: Setup

**Purpose**: Create module skeletons so imports resolve and tasks in later phases can target specific files without ambiguity.

- [ ] T001 Create `frontend/src/engine/math/` directory with empty placeholder files: `types.ts`, `rng.ts`, `tiers.ts`, `generator.ts`, `validator.ts`, `difficulty.ts`, `index.ts`
- [ ] T002 Create `backend/app/mathematics/` domain module with empty `__init__.py`, `types.py`, `rng.py`, `tiers.py`, `generator.py`, `difficulty.py`, `models.py`, `repository.py`, `schemas.py`, `exceptions.py`
- [ ] T003 [P] Create `frontend/tests/engine/math/` directory with empty `generator.test.ts`, `validator.test.ts`, `difficulty.test.ts`
- [ ] T004 [P] Create `backend/tests/unit/mathematics/` and `backend/tests/integration/api/` directories with empty `test_generator.py`, `test_difficulty.py`, `test_problems.py`, `test_difficulty_api.py`

**Checkpoint**: All target files exist; imports will not fail due to missing modules.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, RNG, and tier configs that every user story depends on. No user story implementation can begin until this phase is complete.

**⚠️ CRITICAL**: Phases 3–6 all depend on T005–T010.

- [ ] T005 Define all TypeScript types (`Operation`, `Problem`, `ProblemSet`, `Tier`, `TierConfig`, `ValidationResult`, `TierSelectionInput`) in `frontend/src/engine/math/types.ts` per `data-model.md`
- [ ] T006 [P] Define Python types (`Operation` StrEnum, `Problem` frozen dataclass, `ProblemSet` frozen dataclass) in `backend/app/mathematics/types.py` per `data-model.md`
- [ ] T007 [P] Implement Mulberry32 seeded PRNG as a factory function `createRng(seed: number): () => number` in `frontend/src/engine/math/rng.ts` (research.md Decision 1); verify output is in [0, 1)
- [ ] T008 [P] Implement Python port of Mulberry32 as `create_rng(seed: int)` generator in `backend/app/mathematics/rng.py`; apply 32-bit mask `& 0xFFFFFFFF` after every operation to match JS semantics (research.md Decision 3)
- [ ] T009 [P] Define static `TIER_CONFIGS` map (`Tier → TierConfig`) for tiers 1–5 in `frontend/src/engine/math/tiers.ts`; Tier 6 maps to `null` (data-model.md tier table)
- [ ] T010 [P] Define Python `TIER_CONFIGS` dict for tiers 1–5 in `backend/app/mathematics/tiers.py`; Tier 6 maps to `None`

**Checkpoint**: Foundation ready. All user story work can now begin in parallel.

---

## Phase 3: User Stories 1 + 2 — Core Problem Generator (Priority: P1) 🎯 MVP

**Goal**: `generateProblemSet(tier, seed, count)` returns a deterministic, tier-correct `ProblemSet`. Identical inputs always produce identical output. All tier constraints are enforced. Division is always exact. Subtraction result is always ≥ 0.

**Independent Test**: Generate the same `(tier=2, seed=1234567890, count=8)` twice and assert byte-identical output. Generate 100 problems at Tier 4 and assert all division answers are integers. Run `pnpm test frontend/tests/engine/math/generator.test.ts`.

- [ ] T011 [P] [US1] [US2] Write failing unit tests for problem generation in `frontend/tests/engine/math/generator.test.ts`: determinism (same seed → same sequence), different seed → different sequence, `count=0` returns empty set, Tier 1 = addition-only with operands in [1,10], Tier 4 division answers are integers, subtraction result ≥ 0, operands clamped to tier max
- [ ] T012 [P] [US1] [US2] Write failing Python unit tests in `backend/tests/unit/mathematics/test_generator.py` covering the same invariants as T011 plus 32-bit RNG parity pre-check
- [ ] T013 [US1] [US2] Implement `pickOperation(tier, rng)`, `pickOperands(operation, tierConfig, rng)`, `compute(operation, a, b)` and `generateProblemSet(tier, seed, count, customTierConfig?)` in `frontend/src/engine/math/generator.ts`; Tier 6 fallback to Tier 5 config when `customTierConfig` is absent; subtraction: ensure `operand_a >= operand_b` at generation time (FR-015)
- [ ] T014 [US1] [US2] Implement Python `pick_operation`, `pick_operands`, `compute`, `generate_problem_set` in `backend/app/mathematics/generator.py`; mirror the TypeScript algorithm exactly using `rng.py` and `tiers.py`
- [ ] T015 [US1] [US2] Implement Pydantic request query model and response schema for `/api/v1/problems` in `backend/app/mathematics/schemas.py`; validate `tier` in [1,6], `count` in [0,100], `seed` in [0, 4294967295] (contracts/math-api.md)
- [ ] T016 [US1] [US2] Implement `GET /api/v1/problems` router in `backend/app/presentation/api/v1/problems.py`; delegate to `generate_problem_set`; return HTTP 422 on Pydantic validation failure (contracts/math-api.md)
- [ ] T017 [US1] [US2] Write failing backend integration tests in `backend/tests/integration/api/test_problems.py`: valid request returns 200 with correct shape, `tier=7` returns 422, `count=101` returns 422, parity test (same seed on both Python and TypeScript produces identical `operation/operand_a/operand_b/answer` per problem)
- [ ] T018 [US1] [US2] Export `generateProblemSet` from `frontend/src/engine/math/index.ts`; confirm all T011 tests pass

**Checkpoint**: `generateProblemSet` is fully functional and tested on both sides. The reference API endpoint works. Parity test passes.

---

## Phase 4: User Story 4 — Immediate Answer Validation (Priority: P1)

**Goal**: `validateAnswer(problem, playerInput)` returns a `ValidationResult` in < 1 ms, never throws, correctly identifies correct integers, wrong integers, and non-numeric input. Records elapsed time.

**Independent Test**: Call `validateAnswer` with correct, wrong, and non-numeric inputs; assert results. Run `pnpm test frontend/tests/engine/math/validator.test.ts`.

- [ ] T019 [P] [US4] Write failing unit tests in `frontend/tests/engine/math/validator.test.ts`: correct integer returns `{correct: true}`, wrong integer returns `{correct: false}`, non-numeric returns `{correct: false, reason: 'not_a_number'}`, whitespace-padded input is trimmed and evaluated, `elapsedMs` is a non-negative number
- [ ] T020 [P] [US4] Implement `validateAnswer(problem, playerInput): ValidationResult` in `frontend/src/engine/math/validator.ts`; `parseInt(playerInput.trim())`; record `elapsedMs` as `Date.now()` delta from a `renderTime` argument (passed by the caller when the problem is rendered)
- [ ] T021 [P] [US4] Export `validateAnswer` from `frontend/src/engine/math/index.ts`; confirm all T019 tests pass

**Checkpoint**: Answer validation is independently functional and tested.

---

## Phase 5: User Story 3 — Consecutive Duplicate Prevention (Priority: P2)

**Goal**: No two consecutive problems in a `ProblemSet` share `(operation, operand_a, operand_b)`. After 10 retries the duplicate is accepted (loop safety).

**Independent Test**: Generate 500 problems at Tier 1 (most constrained) and scan for consecutive identical tuples. Run `pnpm test frontend/tests/engine/math/generator.test.ts`.

- [ ] T022 [US3] Add `isDuplicate(candidate, last)` helper and retry loop (max 10 retries per slot) to `frontend/src/engine/math/generator.ts`; retry count resets per slot
- [ ] T023 [US3] Add duplicate-prevention test cases to `frontend/tests/engine/math/generator.test.ts`: no consecutive identical tuple in a 500-problem Tier 1 set; loop terminates when retry limit is reached (mock constrained tier)
- [ ] T024 [US3] Add equivalent retry logic to `backend/app/mathematics/generator.py` and corresponding test cases to `backend/tests/unit/mathematics/test_generator.py`

**Checkpoint**: Duplicate prevention works and is verified. All prior story tests still pass.

---

## Phase 6: User Story 5 — Adaptive Tier Selection (Priority: P2)

**Goal**: `selectTier` returns the correct tier based on skill score thresholds and parent override. The backend stores and serves the player's current tier and parent override. The tier never changes during an active race (enforced by callers; the engine returns a value, it does not mutate state).

**Independent Test**: Call `selectTier` with all boundary inputs; assert output. Call `GET/PATCH /api/v1/players/{id}/difficulty`; assert responses. Run `pnpm test frontend/tests/engine/math/difficulty.test.ts` and `pytest tests/integration/api/test_difficulty_api.py`.

- [ ] T025 [P] [US5] Write failing unit tests for `selectTier` in `frontend/tests/engine/math/difficulty.test.ts`: skill ≥ 0.90 → tier+1 (capped at 6), skill < 0.60 → tier-1 (floored at 1), 0.60 ≤ skill < 0.90 → unchanged, parent override returns clamped override regardless of skill score, override outside [1,6] is clamped silently
- [ ] T026 [P] [US5] Write failing Python unit tests for `select_tier` in `backend/tests/unit/mathematics/test_difficulty.py` covering the same cases as T025
- [ ] T027 [P] [US5] Implement `selectTier(input: TierSelectionInput): Tier` in `frontend/src/engine/math/difficulty.ts`; clamp `parentOverride` to [1,6] if provided (FR-008, FR-009)
- [ ] T028 [P] [US5] Implement `select_tier(current_tier, skill_score, parent_override)` function in `backend/app/mathematics/difficulty.py`
- [ ] T029 [US5] Create `PlayerDifficulty` SQLAlchemy ORM model (`player_id` FK, `current_tier` int, `parent_override` nullable int, `updated_at`) in `backend/app/mathematics/models.py`
- [ ] T030 [US5] Create Alembic migration `add_player_difficulty` in `backend/alembic/versions/`; include rollback `downgrade()` function
- [ ] T031 [US5] Implement `PlayerDifficultyRepository` protocol and `SQLAlchemyPlayerDifficultyRepository` in `backend/app/mathematics/repository.py` (get by player_id, upsert)
- [ ] T032 [US5] Add difficulty request/response Pydantic schemas to `backend/app/mathematics/schemas.py` (contracts/math-api.md `GET/PATCH /api/v1/players/{id}/difficulty`)
- [ ] T033 [US5] Add `PlayerNotFoundError` to `backend/app/mathematics/exceptions.py`
- [ ] T034 [US5] Implement `GET /api/v1/players/{id}/difficulty` and `PATCH /api/v1/players/{id}/difficulty` routers in `backend/app/presentation/api/v1/difficulty.py`; derive `effective_tier` at read time; validate `parent_override` in [1,6] or null; return 422 on out-of-range value; return 404 for unknown player; enforce authentication + parent-only authorization for PATCH
- [ ] T035 [US5] Write integration tests in `backend/tests/integration/api/test_difficulty_api.py`: GET returns current tier, PATCH sets override, PATCH null clears override, PATCH with value 7 returns 422, unknown player returns 404, unauthenticated request returns 401
- [ ] T036 [US5] Export `selectTier` from `frontend/src/engine/math/index.ts`; confirm all T025 tests pass

**Checkpoint**: Tier selection is fully functional on both sides, backed by persistent storage. All prior story tests still pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Wire everything together, validate end-to-end, and update documentation.

- [ ] T037 [P] Register `problems` and `difficulty` routers in `backend/app/presentation/api/v1/` router registry (or `backend/app/main.py` depending on existing pattern); confirm routes are discoverable via OpenAPI at `/api/v1/openapi.json`
- [ ] T038 [P] Add structured error logging (FR-014) to `generator.py` / `generator.ts`: log on retry-limit exhaustion (duplicate accepted) and on unexpected non-numeric validation input exceeding a threshold
- [ ] T039 Run quickstart.md Scenario 5 (frontend ↔ backend parity check) manually and confirm all 5 problem fields match for `tier=3, seed=777, count=5`
- [ ] T040 [P] Update `docs/gameplay/spec-math-engine.md` if any implemented behaviour diverges from the spec (Constitution §XX)
- [ ] T041 Run `pnpm test frontend/tests/engine/math/` and `pytest backend/tests/unit/mathematics/ backend/tests/integration/api/test_problems.py backend/tests/integration/api/test_difficulty_api.py` — confirm zero failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks all user story phases**
- **Phase 3 (US1+US2)**: Depends on Phase 2
- **Phase 4 (US4)**: Depends on Phase 2 — **independent of Phase 3**
- **Phase 5 (US3)**: Depends on Phase 3 (extends the generator)
- **Phase 6 (US5)**: Depends on Phase 2 (uses types); independent of Phases 3–5
- **Phase 7 (Polish)**: Depends on Phases 3–6

### User Story Dependencies

| Story | Depends on | Blocks |
|---|---|---|
| US1 + US2 (Phase 3) | Phase 2 | Phase 5 (US3) |
| US4 (Phase 4) | Phase 2 | — |
| US3 (Phase 5) | Phase 3 | — |
| US5 (Phase 6) | Phase 2 | — |

### Within Each Phase

- Tests (T011–T012, T019, T022–T023, T025–T026) should be written first and verified to fail before implementation
- Types/models before services
- Services before API endpoints
- Core implementation before registration/wiring (Phase 7)

---

## Parallel Execution Examples

### Phase 2 — All foundational tasks are parallel

```
T005 (TypeScript types)      ──┐
T006 (Python types)          ──┤
T007 (TS RNG)                ──┤→ all can run concurrently
T008 (Py RNG)                ──┤
T009 (TS tier configs)       ──┤
T010 (Py tier configs)       ──┘
```

### Phase 3 vs Phase 4 — Can run in parallel after Phase 2

```
Phase 3 (US1+US2 generator)  ──┐
                               ├→ concurrent
Phase 4 (US4 validator)      ──┘
```

### Phase 6 — Frontend and backend difficulty work is parallel

```
T025 (TS difficulty tests)   ──┐
T026 (Py difficulty tests)   ──┤
T027 (selectTier TS)         ──┤→ all can run concurrently
T028 (select_tier Py)        ──┘
```

---

## Implementation Strategy

### MVP (User Stories 1 + 2 only — Phase 1 → Phase 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: Core generator (US1 + US2)
4. **STOP and VALIDATE**: Run generator tests; run parity scenario from quickstart.md
5. The engine generates correct, deterministic, tier-appropriate problems — MVP ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Phase 3 → deterministic generation works (**MVP**)
3. Phase 4 → answer validation works (US4, independent)
4. Phase 5 → no consecutive duplicates (US3)
5. Phase 6 → adaptive tier selection + parent override API (US5)
6. Phase 7 → wired, logged, documented, all tests green

### Parallel Team Strategy

After Phase 2 completes, three streams can proceed independently:

- **Stream A**: Phase 3 (generator, reference API)
- **Stream B**: Phase 4 (validator)
- **Stream C**: Phase 6 (difficulty service, DB, API)

Phase 5 (US3) merges into Stream A after Phase 3 completes.

---

## Notes

- All `[P]` tasks target different files and have no dependency on incomplete sibling tasks
- `[US1]` and `[US2]` are combined in Phase 3 — their generator implementations are inseparable at the code level
- Tests must fail before implementation is written; assert failure in CI before merging
- Commit after each checkpoint (end of each phase) at minimum
- The parity integration test (T017) is the single most valuable test — it proves both sides of the engine agree
- Tier 6 custom config injection is a function parameter, not global state — keep it that way
