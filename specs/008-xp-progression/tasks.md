# Tasks: XP & Player Progression

**Input**: Design documents from `specs/008-xp-progression/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Module Skeleton)

**Purpose**: Create the new `app/progression` module structure and test package scaffolding so all downstream tasks can import and reference paths without errors.

- [ ] T001 Create backend/app/progression/ module and all __init__.py files for backend/app/progression/, backend/app/progression/presentation/, backend/app/progression/presentation/api/, backend/app/progression/presentation/api/v1/, backend/tests/unit/progression/, backend/tests/integration/progression/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database migration and core domain layer — models, repository, domain service, and schemas that all user stories depend on. No user story can be implemented until this phase is complete.

**⚠️ CRITICAL**: All of Phase 2 must complete before any user story work begins.

- [ ] T002 [P] Write Alembic migration in backend/alembic/versions/0008_add_progression.py: create `player_progressions` table (account_id PK FK→accounts, total_xp int NOT NULL DEFAULT 0, current_level int NOT NULL DEFAULT 0, updated_at timestamptz DEFAULT now()); create `xp_events` table (id UUID PK, account_id FK→accounts ON DELETE CASCADE, source varchar CHECK IN ('race_completion','correct_answer','streak_bonus','championship_bonus'), amount int CHECK amount > 0, race_id UUID FK→races ON DELETE SET NULL nullable, created_at timestamptz DEFAULT now()); add column `longest_streak integer NOT NULL DEFAULT 0` to `race_participants`; add indexes idx_xp_events_account_id, idx_xp_events_race_id
- [ ] T003 [P] Create PlayerProgression and XPEvent SQLAlchemy mapped models in backend/app/progression/models.py following the pattern in backend/app/races/models.py; PlayerProgression has account_id as PK (UUID FK→accounts CASCADE); XPEvent has UUID PK with gen_random_uuid() default, account_id FK, source String with CheckConstraint, amount Integer with CheckConstraint > 0, race_id nullable FK→races SET NULL, created_at; add indexes matching data-model.md
- [ ] T004 [P] Create Pydantic schemas in backend/app/progression/schemas.py: LevelUpEvent(previous_level: int, new_level: int, total_xp: int); ProgressionResponse(total_xp: int, current_level: int, xp_to_next_level: int, xp_earned_this_race: int | None = None, level_up: LevelUpEvent | None = None); follow existing schema style from backend/app/races/schemas.py
- [ ] T005 Implement ProgressionRepository in backend/app/progression/repository.py: Protocol with get(account_id) -> PlayerProgression | None; upsert(account_id, xp_delta, new_total, new_level) -> PlayerProgression; insert_event(account_id, source, amount, race_id) -> None; SQLAlchemyProgressionRepository implementing the protocol using the same session pattern as backend/app/races/repository.py; upsert uses INSERT INTO player_progressions ... ON CONFLICT (account_id) DO UPDATE
- [ ] T006 Implement ProgressionDomainService in backend/app/progression/domain_service.py with two methods: (1) award_xp(account_id, problems_correct, longest_streak, mode, race_id) -> ProgressionResponse — calculates delta using formula race_xp=100 + correct_xp=problems_correct*20 + streak_xp=floor(longest_streak/5)*10 + mode_bonus=500 if mode=='championship' else 0, fetches or initialises progression, upserts new total, inserts one XPEvent with source='race_completion', detects level-up by comparing floor(sqrt(old_total/100)) vs floor(sqrt(new_total/100)), returns ProgressionResponse; (2) get_progression(account_id) -> ProgressionResponse — returns current state or zero-state if no row exists; level formula: current_level = floor(sqrt(total_xp / 100)); xp_to_next_level = (current_level+1)**2 * 100 - total_xp; xp_to_next_level must never be < 1

**Checkpoint**: Migration + domain layer complete. ProgressionDomainService is unit-testable independently.

---

## Phase 3: User Story 1 — Earn XP After a Race (Priority: P1) 🎯 MVP

**Goal**: When a player submits a race result via POST /api/v1/races, XP is calculated and credited within the same transaction. The response includes the updated progression and any level-up event.

**Independent Test**: Submit POST /api/v1/races with known inputs, verify response.progression.xp_earned_this_race equals the expected formula result, total_xp increases, and level_up fires when a boundary is crossed.

- [ ] T007 [P] [US1] Add `longest_streak: Mapped[int]` column to RaceParticipant in backend/app/races/models.py: `longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)` with a CheckConstraint `longest_streak >= 0`; follow existing column style
- [ ] T008 [P] [US1] Update backend/app/races/schemas.py: add `longest_streak: Annotated[int, Field(ge=0)]` to ParticipantSummaryRequest; add `progression: ProgressionResponse | None = None` to RaceSummaryResponse; import ProgressionResponse from app.progression.schemas
- [ ] T009 [US1] Update backend/app/races/domain_service.py: modify RaceDomainService.__init__ to accept an optional second argument `progression_repository: ProgressionRepository | None = None`; modify persist_race signature to accept `account_id: uuid.UUID | None = None`; after await self._repository.create(request) succeeds (race newly created), if both account_id and progression_repository are provided, instantiate ProgressionDomainService(progression_repository) and call award_xp using the player participant's (position==1 or first participant) problems_correct and longest_streak, the race mode, and race_id; attach result to RaceSummaryResponse.progression; import ProgressionDomainService and ProgressionRepository from app.progression
- [ ] T010 [US1] Update backend/app/races/presentation/api/v1/races.py: instantiate SQLAlchemyProgressionRepository(session) alongside the existing SQLAlchemyRaceRepository(session); pass progression_repository to RaceDomainService; pass account.id to service.persist_race(body, account_id=account.id); update response_model to RaceSummaryResponse (already correct, just ensure progression field is included)
- [ ] T011 [US1] Write integration tests in backend/tests/integration/progression/test_api_progression.py: test_xp_awarded_on_race_submission — submit POST /api/v1/races with problems_correct=7 longest_streak=5 mode=quick, assert response 201 and progression.xp_earned_this_race == 250 (100+140+10) and progression.total_xp == 250 and progression.current_level == 1 and progression.level_up.previous_level == 0; test_duplicate_race_returns_409_and_no_double_xp — submit same race_id twice, assert second returns 409, then GET /api/v1/progression and verify total_xp unchanged; follow the _register_and_approve() helper pattern from backend/tests/integration/championships/test_api_championships.py

**Checkpoint**: US1 fully functional. POST /api/v1/races returns progression data with XP earned and level-up detection.

---

## Phase 4: User Story 2 — View Current Progression (Priority: P2)

**Goal**: Any authenticated player can GET their current XP total, level, and next-level threshold at any time without submitting a race.

**Independent Test**: Seed a player with known XP by submitting a race, then call GET /api/v1/progression and verify total_xp, current_level, xp_to_next_level all match expected formula values. Also verify zero-state for a fresh account.

- [ ] T012 [US2] Implement GET /api/v1/progression router in backend/app/progression/presentation/api/v1/progression.py: router prefix `/api/v1/progression` tag `progression`; single GET "" endpoint returning ProgressionResponse with status 200; inject get_current_account and get_session; instantiate SQLAlchemyProgressionRepository(session) and ProgressionDomainService(repo); call service.get_progression(account.id); follow pattern of backend/app/races/presentation/api/v1/races.py
- [ ] T013 [US2] Register progression router in backend/app/main.py: import `from app.progression.presentation.api.v1.progression import router as progression_router` inside create_app() alongside other router imports; call `app.include_router(progression_router)`
- [ ] T014 [US2] Add integration tests to backend/tests/integration/progression/test_api_progression.py: test_get_progression_zero_state — fresh account with no races, GET /api/v1/progression returns 200 with total_xp=0, current_level=0, xp_to_next_level=100; test_get_progression_after_race — submit a race then GET /api/v1/progression, assert values match race submission response; test_progression_unauthenticated — GET /api/v1/progression without token returns 401

**Checkpoint**: US1 + US2 fully functional. Players can earn and view progression.

---

## Phase 5: User Story 3 — Championship Race Bonus XP (Priority: P3)

**Goal**: Championship mode awards 500 bonus XP on top of standard race XP, verified by dedicated tests.

**Independent Test**: Submit POST /api/v1/races with mode=championship and known inputs, verify mode_bonus=500 is included in xp_earned_this_race.

- [ ] T015 [US3] Write unit tests for ProgressionDomainService in backend/tests/unit/progression/test_domain_service.py: test_xp_formula_quick_race — mock repository, call award_xp with problems_correct=5 longest_streak=0 mode='quick', assert xp_earned=200; test_xp_formula_championship_bonus — mode='championship', assert xp_earned=700 (100+100+500); test_xp_formula_streak_bonus — longest_streak=10, assert streak_xp=20 (floor(10/5)*10); test_level_formula — assert floor(sqrt(x/100)) for boundary values (0→0, 100→1, 400→2, 900→3); test_level_up_detected — award XP that crosses level boundary, assert returned level_up is not None with correct previous/new levels; test_no_level_up — award XP within same level, assert level_up is None; test_xp_to_next_level_never_negative — verify xp_to_next_level >= 1 for a range of total_xp values; use unittest.mock.AsyncMock for repository
- [ ] T016 [US3] Add championship integration test to backend/tests/integration/progression/test_api_progression.py: test_championship_bonus_xp — submit race with mode=championship problems_correct=5 longest_streak=0, assert xp_earned_this_race == 700 (100 + 100 + 500)

**Checkpoint**: All three user stories fully implemented and tested.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T017 Add structured logging calls in backend/app/progression/domain_service.py for XP award events (log account_id, xp_delta, new_total, new_level, level_up bool) and level-up events; use get_logger(__name__) following the pattern in backend/app/avatars/generation_service.py
- [ ] T018 Run scripts/run-local-ci-checks.sh from backend/ and fix any failures (mypy, black, integration tests)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — modifies races layer to call progression service
- **Phase 4 (US2)**: Depends on Phase 2 — read endpoint uses same domain service
- **Phase 5 (US3)**: Depends on Phase 2 (unit tests) and Phase 3 (integration test)
- **Phase 6 (Polish)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1)**: Requires Phase 2 complete; modifies races domain layer
- **US2 (P2)**: Requires Phase 2 complete; independent of US1 (read path doesn't require write path)
- **US3 (P3)**: Tests only; requires Phase 2 (unit) and Phase 3 (integration)

### Within Each Phase

- T002, T003, T004 can run in parallel (separate files)
- T005 depends on T003 (imports models)
- T006 depends on T003, T004, T005
- T007, T008 can run in parallel (separate files)
- T009 depends on T006, T007, T008
- T010 depends on T009
- T011 depends on T010 (requires running stack)
- T012 depends on T006
- T013 depends on T012
- T014 depends on T013 (requires running stack)
- T015 depends on T006 (unit tests the domain service)
- T016 depends on T011 (integration layer must be working)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# These three tasks can run simultaneously:
Task T002: Write migration 0008_add_progression.py
Task T003: Create progression/models.py
Task T004: Create progression/schemas.py

# Then sequentially:
Task T005: ProgressionRepository (uses models from T003)
Task T006: ProgressionDomainService (uses models, schemas, repository)
```

## Parallel Example: Phase 3 (US1 setup)

```bash
# These two tasks can run simultaneously:
Task T007: Add longest_streak to RaceParticipant model
Task T008: Update races schemas (add longest_streak + ProgressionResponse)

# Then sequentially:
Task T009: RaceDomainService integration (uses T007 + T008)
Task T010: Races router update
Task T011: Integration tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Module scaffold
2. Complete Phase 2: Migration + models + repository + domain service
3. Complete Phase 3: Wire into races endpoint
4. **STOP and VALIDATE**: POST a race, verify progression in response
5. Run integration tests for US1

### Incremental Delivery

1. Phase 1 + Phase 2 → Progression engine ready (not yet exposed)
2. Phase 3 (US1) → POST /api/v1/races now returns XP data (MVP!)
3. Phase 4 (US2) → GET /api/v1/progression endpoint live
4. Phase 5 (US3) → Championship bonus verified with tests
5. Phase 6 (Polish) → Logging + CI clean

---

## Notes

- [P] tasks touch different files — no merge conflicts
- Unit tests (T015) mock the repository with `unittest.mock.AsyncMock` — no DB needed
- Integration tests follow the `_register_and_approve()` helper pattern from existing test files
- The XP formula is pure arithmetic — deterministic and fully unit-testable
- `longest_streak` is a new required field on `ParticipantSummaryRequest` — existing tests may need updating if they don't include it
