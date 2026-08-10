# Tasks: Game Modes

**Input**: Design documents from `specs/006-game-modes/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Note on tests**: Included per Constitution §XVIII (tests mandatory for every feature). Not TDD-framed — write alongside implementation.

**Organization**: 4 user stories (US1–US4) in priority order after a shared Foundational phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story this task belongs to

---

## Phase 1: Setup

No new tooling or project scaffolding required. Project structure is in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema changes and type updates that every user story depends on.

**⚠️ CRITICAL**: Complete before any user story phase begins.

- [x] T001 Write Alembic migration for nullable `position` on `race_participants` and new `championships` + `championship_races` tables in `backend/alembic/versions/0006_game_modes.py`
- [x] T002 [P] Update `RaceParticipant.position` to nullable with `CHECK (position IS NULL OR position BETWEEN 1 AND 5)` in `backend/app/races/models.py`
- [x] T003 [P] Update `ParticipantSummaryRequest.position` to `Optional[int]` and add cross-field validation (null only when `mode == "training"`) in `backend/app/races/schemas.py`
- [x] T004 [P] Update `ParticipantSummary.position` to `number | null` in `frontend/src/engine/race/types.ts`

**Checkpoint**: Migration written; backend races accepts null position for training; frontend type widened.

---

## Phase 3: User Story 1 — Quick Race XP (Priority: P1) 🎯 MVP

**Goal**: XP is calculated and submitted correctly for Quick Race results; the existing race submission flow is complete end-to-end.

**Independent Test**: Run a Quick Race with 3 opponents; verify `xp_earned` in the submitted payload equals 10 × correct answers.

- [x] T005 [US1] Implement per-mode XP formula in `getSummary()` in `frontend/src/engine/race/raceEngine.ts` (Quick Race / Duel: 10 XP per correct answer; see data-model.md XP table)
- [x] T006 [US1] Unit tests for XP formula per mode (quick, duel) in `frontend/tests/engine/race/raceEngine.integration.test.ts`

**Checkpoint**: Quick Race result submission includes correct `xp_earned` values. US1 independently testable.

---

## Phase 4: User Story 2 — Championship Series (Priority: P2)

**Goal**: A player can start a championship, record race results with standings updates, and resume after a browser close. Championship auto-completes on the final race.

**Independent Test**: POST a championship (3 races), PATCH 3 race results in sequence; verify final response has `status: "completed"` and standings reflect cumulative points in correct order.

- [ ] T007 [P] [US2] Create `backend/app/championships/` package (`__init__.py`) and `Championship` + `ChampionshipRace` SQLAlchemy models in `backend/app/championships/models.py`
- [ ] T008 [P] [US2] Create Pydantic schemas (`CreateChampionshipRequest`, `RecordRaceRequest`, `ChampionshipResponse`, `StandingEntry`) in `backend/app/championships/schemas.py`
- [ ] T009 [US2] Implement `ChampionshipRepository` (Protocol + `SQLAlchemyChampionshipRepository`) in `backend/app/championships/repository.py` (depends on T007)
- [ ] T010 [US2] Implement `ChampionshipDomainService` with points table (10/6/3/1/0), standings calculation, podium count, and auto-complete logic in `backend/app/championships/domain_service.py` (depends on T008, T009)
- [ ] T011 [US2] Implement `POST /api/v1/championships`, `GET /api/v1/championships/{id}`, and `PATCH /api/v1/championships/{id}/races/{race_id}` router in `backend/app/presentation/api/v1/championships.py` (depends on T010)
- [ ] T012 [US2] Register championships router in `backend/app/main.py` (depends on T011)
- [ ] T013 [P] [US2] Unit tests for `ChampionshipDomainService`: points table values, standings sort order, podium counting, auto-complete on final race in `backend/tests/unit/championships/test_domain_service.py`
- [ ] T014 [US2] Integration tests for POST/GET/PATCH championship endpoints (happy path, ownership guard, 409 duplicate race, auto-complete on final race) in `backend/tests/integration/championships/test_api_championships.py` (depends on T012)
- [ ] T015 [P] [US2] Frontend championship API client (`createChampionship`, `getChampionship`, `recordChampionshipRace`) in `frontend/src/engine/race/championshipApi.ts`

**Checkpoint**: All three championship endpoints functional with ownership auth; auto-complete works; standings return in correct order. US2 independently testable.

---

## Phase 5: User Story 3 — Training Mode (Priority: P3)

**Goal**: Training runs without a finish line; the player can exit voluntarily; a partial result is submitted with `position: null` and training-appropriate XP.

**Independent Test**: Create a race engine with `mode: "training"`, answer 5 problems, call `forceComplete()`; verify `getSummary()` returns `position: null` for the human runner and `xp_earned = 5 * 5 = 25`.

- [ ] T016 [US3] Add `forceComplete()` method to `RaceEngine` interface and `createRaceEngine` factory; implement training-mode `getSummary()` branch with `position: null` and training XP (5 XP per correct answer) in `frontend/src/engine/race/raceEngine.ts`
- [ ] T017 [US3] Expose `forceComplete()` from `useRaceEngine` hook so the UI can trigger a training exit in `frontend/src/engine/race/hooks/useRaceEngine.ts`
- [ ] T018 [US3] Unit tests for training exit: `forceComplete()` transition, null position in summary, training XP formula, no race-completion XP in `frontend/tests/engine/race/raceEngine.test.ts`
- [ ] T019 [US3] Integration test: `POST /api/v1/races` with `mode: "training"` and `position: null` returns 201 in `backend/tests/integration/races/test_api_races.py`

**Checkpoint**: Training mode exits cleanly; partial result submitted with correct shape. US3 independently testable.

---

## Phase 6: User Story 4 — Duel Mode (Priority: P3)

**Goal**: Duel creates exactly one AI opponent whose difficulty tier matches the player's current adaptive tier (clamped to minimum 1, Balanced personality).

**Independent Test**: Call `buildDuelConfig(playerTier)` for tiers 1–6; verify output always has exactly one AI participant with Balanced personality and `tier = clamp(playerTier, 1, 6)`.

- [ ] T020 [US4] Create `buildDuelConfig(playerTier: Tier): ParticipantConfig[]` helper that selects the Balanced personality and clamps the tier to minimum 1 in `frontend/src/engine/race/duelConfig.ts`
- [ ] T021 [US4] Unit tests for duel config: tier clamping at boundaries (tier 1, tier 6), correct personality selected, exactly one AI participant in `frontend/tests/engine/race/duelConfig.test.ts`

**Checkpoint**: `buildDuelConfig` produces correct participant config for all valid tier values. US4 independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T022 [P] Create `backend/tests/unit/championships/__init__.py` and `backend/tests/integration/championships/__init__.py` (package init files for test discovery — if not already created in T013/T014)
- [ ] T023 [P] Mark acceptance criteria checkboxes in `docs/gameplay/spec-game-modes.md` as implemented once all phases pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 2 (Foundational)**: No dependencies — start immediately
- **Phase 3 (US1)**: Depends on T004 (frontend type widening only); T005–T006 can start once T004 is done
- **Phase 4 (US2)**: Depends on T001 (migration) and T004; T007–T008 can start after T001
- **Phase 5 (US3)**: Depends on T002, T003, T004; T016 can start after T002–T004
- **Phase 6 (US4)**: No foundational blockers beyond T004; T020 can start at any time
- **Phase 7 (Polish)**: After all desired stories complete

### Within Each Phase

- T007 and T008 are parallel (different files); T009 depends on T007; T010 depends on T008+T009
- T013 can be written alongside T010 (same logic, test-first optional)
- T016 and T017 are sequential (T017 depends on the `forceComplete()` interface from T016)

### Parallel Opportunities (within Phase 4)

```
T007 [championships/models.py]    ─┐
T008 [championships/schemas.py]   ─┤→ T009 → T010 → T011 → T012 → T014
T015 [championshipApi.ts]        ─┘ (frontend: independent of T009–T014)
T013 [unit tests]                ← write alongside T010
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 2 (Foundational)
2. Complete Phase 3 (US1: XP wiring)
3. **Validate**: Quick Race submits correct XP; idempotency via existing 409 behavior confirmed
4. Stop and demo

### Incremental Delivery

1. Phase 2 → Foundation ready
2. Phase 3 (US1) → Quick Race complete ✓
3. Phase 4 (US2) → Championship complete ✓
4. Phase 5 (US3) → Training complete ✓
5. Phase 6 (US4) → Duel complete ✓
6. Phase 7 → Polish ✓

### Parallel Team Strategy

After Phase 2:
- **Backend developer**: T007 → T009 → T010 → T011 → T012 → T013 → T014 (Championship backend)
- **Frontend developer A**: T005 → T006 (US1 XP) then T015 (Championship API client)
- **Frontend developer B**: T016 → T017 → T018 (US3 Training) then T020 → T021 (US4 Duel)

---

## Notes

- [P] tasks target different files and have no incomplete dependencies — safe to run in parallel
- [Story] label maps each task to its user story for traceability
- T001 (migration) is the single highest-risk task — review SQL carefully before applying
- Quickstart.md scenarios 1–5 serve as manual end-to-end verification after each phase
- Avatar guard (FR-002) is a no-op stub until the Avatar feature ships — no task needed here
