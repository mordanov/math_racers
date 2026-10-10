# Tasks: Audit Remediation

**Input**: Design documents in `specs/014-audit-remediation/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and
`contracts/race-and-child-data.md`

## Execution rules

- Finish each focused test task and confirm that it fails for the reported gap
  before implementing its fix.
- Run the narrow test set after each dependent slice.
- Keep every D-01 through D-14 item and every R-01 through R-08 decision in
  scope. Do not mark an item done without recorded test or environment evidence.
- Use the Constitution's source order. Update approved source and derived
  requirements before changing application behaviour.
- The task order is a dependency order, not permission to omit tasks when the
  10-day estimate is exceeded.

## Phase 1: Setup and approved requirements

**Purpose**: Record the approved decisions in authoritative and derived
requirements before implementation.

- [X] T001 Update the approved rules and resolve R-01 through R-08 in `initial_spec/gdd.md` and `initial_spec/game_economy_specification.md`.
- [X] T002 [P] Align game-mode, race, and operation rules with the approved requirements in `docs/gameplay/feature-game-modes.md`, `docs/gameplay/spec-game-modes.md`, `docs/gameplay/feature-math-engine.md`, and `docs/gameplay/spec-math-engine.md`.
- [X] T003 [P] Align XP, championship, daily-challenge, statistics, and achievement requirements in `docs/economy/feature-xp-progression.md`, `docs/economy/spec-xp-progression.md`, `docs/economy/feature-statistics.md`, `docs/economy/spec-statistics.md`, and `docs/economy/spec-achievements.md`.
- [X] T004 [P] Record blocking image-safety, AI-provider, storage, security, and offline requirements in `docs/content/spec-avatar-generation.md`, `docs/ai/asset-pipeline.md`, `docs/ai/ai-architecture.md`, and `docs/engineering/technical-requirements.md`.
- [X] T005 Update the public race and child-data API rules in `docs/gameplay/spec-game-modes.md` and `specs/014-audit-remediation/contracts/race-and-child-data.md`.
- [X] T006 Record each approved rule and its source in `specs/014-audit-remediation/research.md` and `specs/014-audit-remediation/spec.md`.
- [X] T007 Run and record the existing focused backend and frontend baseline tests for races, child profiles, progression, statistics, achievements, and avatar generation.

## Phase 2: Foundational data and ownership

**Purpose**: Add the child identity and safe schema foundation required by
race, progress, statistics, achievement, avatar, and offline work.

- [X] T008 [P] Add failing migration tests for legacy records and reversible child ownership in `backend/tests/integration/test_audit_remediation_migration.py`.
- [X] T009 [P] Add failing child-context and cross-profile authorization tests in `backend/tests/unit/middleware/test_child_profile_middleware.py`.
- [X] T010 Add nullable child ownership, result identity, and required uniqueness constraints in a new reversible migration under `backend/alembic/versions/`.
- [X] T011 Update child-owned SQLAlchemy entities and repository filters in `backend/app/avatars/models.py`, `backend/app/races/models.py`, `backend/app/progression/models.py`, `backend/app/statistics/models.py`, and `backend/app/achievements/models.py`.
- [X] T012 Implement shared active-child resolution and parent ownership validation in `backend/app/presentation/api/middleware/child_profile.py` and `backend/app/child_profiles/repository.py`.
- [X] T013 Verify upgrade, downgrade, preservation of unassigned legacy rows, and child invisibility in `backend/tests/integration/test_audit_remediation_migration.py`.

## Phase 3: User Story 1 - Complete a race and keep correct results (Priority: P1)

**Goal**: Implement a separate session and result API, identify the human from
the persisted session, and make result processing atomic and idempotent.

**Independent Test**: Create a session, submit a result with an AI ranked
first, and repeat the same result. Verify one human-owned result and one set of
rewards and statistics.

- [X] T014 [P] [US1] Add failing contract and integration tests for race creation, result submission, human identity, and safe retries in `backend/tests/integration/races/test_api_races.py`.
- [X] T015 [P] [US1] Add failing frontend contract tests for separate session and result calls in `frontend/src/features/race/raceSessionApi.test.ts`.
- [X] T016 [US1] Define race session, participant, answer, and idempotency request/response schemas in `backend/app/races/schemas.py`.
- [X] T017 [US1] Persist the race session, selected child, human avatar, mode, tier, seed, and status in `backend/app/races/models.py` and `backend/app/races/repository.py`.
- [X] T018 [US1] Add distinct create-session and submit-result routes in `backend/app/races/presentation/api/v1/races.py`.
- [X] T019 [US1] Implement the transactional race-result application use case in `backend/application/submit_race_result.py`.
- [X] T020 [US1] Persist the idempotency key and return the original result for safe retries in `backend/app/races/repository.py` and `backend/application/submit_race_result.py`.
- [X] T021 [US1] Bind the selected child and human avatar to session setup and result submission in `frontend/src/features/race/raceSessionApi.ts`, `frontend/src/engine/race/types.ts`, and `frontend/src/pages/RaceSetupPage.tsx`.
- [X] T022 [US1] Update race result handling and regression coverage in `frontend/src/pages/ResultsScreenPage.tsx` and `frontend/src/pages/ResultsScreenPage.test.tsx`.
- [X] T023 [US1] Run the race API, application-use-case, and frontend race-session tests and record D-01, D-03, and D-13 evidence.

## Phase 4: User Story 2 - Keep each child's data separate (Priority: P1)

**Goal**: Enforce ownership at every child-data boundary and give parents an
explicit, atomic way to assign unowned legacy records, export child data, and
delete one child's data.

**Independent Test**: Use two child profiles and legacy records. Prove that
each child sees only assigned data and that a parent can assign, export, and
delete data for one child only.

- [X] T024 [P] [US2] Add failing tests for cross-child reads, writes, exports, deletes, and legacy assignment in `backend/tests/integration/child_profiles/test_api_child_profiles.py`.
- [X] T025 [P] [US2] Add failing frontend tests for selecting and assigning legacy records in `frontend/src/pages/ParentDashboardPage.test.tsx`.
- [X] T026 [US2] Add parent-only legacy-data listing and atomic assignment use cases in `backend/application/assign_legacy_child_data.py` and `backend/app/child_profiles/repository.py`.
- [X] T027 [US2] Add legacy-data listing and assignment endpoints with parent ownership checks in `backend/app/child_profiles/presentation/api/v1/child_profiles.py`.
- [X] T028 [US2] Scope avatar reads, writes, and generation to the selected child in `backend/app/avatars/repository.py`, `backend/app/avatars/schemas.py`, and `backend/app/avatars/presentation/api/v1/avatars.py`.
- [X] T029 [US2] Scope race, progression, statistics, and achievement reads and writes to the selected child in `backend/app/races/repository.py`, `backend/app/progression/repository.py`, `backend/app/statistics/repository.py`, and `backend/app/achievements/repository.py`.
- [X] T030 [US2] Implement parent-authorized child data export and deletion with child-scoped cascade behaviour in `backend/application/` and `backend/app/child_profiles/presentation/api/v1/child_profiles.py`.
- [X] T031 [US2] Send the active child ID through the shared client and handle parent-only profile actions in `frontend/src/infrastructure/auth/AuthContext.tsx`, `frontend/src/infrastructure/api-client.ts`, and `frontend/src/pages/ParentDashboardPage.tsx`.
- [X] T032 [US2] Run child-profile API, migration, ownership, export, deletion, and frontend tests and record D-02 evidence.

## Phase 5: User Story 3 - Use Training and progression rules (Priority: P1)

**Goal**: Apply the approved Training, XP, level, tier, and championship
behaviour in the browser and backend.

**Independent Test**: Complete more than eight Training answers, exit without
race completion, and verify answer XP, zero race XP, operation tiers, Tier 6
settings, and one championship completion award.

- [X] T033 [P] [US3] Add failing domain tests for open-ended Training, answer XP, level baseline, and one-time championship XP in `backend/tests/unit/progression/test_domain_service.py`.
- [X] T034 [P] [US3] Add failing frontend tests for Training duration and approved tiers in `frontend/src/engine/race/hooks/useRaceEngine.test.ts` and `frontend/src/engine/math/tiers.test.ts`.
- [X] T035 [US3] Implement approved XP, Level 1 baseline, and championship completion rewards in `backend/app/progression/domain_service.py` and `backend/app/progression/repository.py`.
- [X] T036 [US3] Store operation and correctness details for every answer in `backend/app/races/schemas.py`, `backend/app/races/models.py`, and the migration in `backend/alembic/versions/`.
- [X] T037 [US3] Implement an unlimited Training loop with no opponents, timer, finish line, or race-completion reward in `frontend/src/engine/race/raceEngine.ts` and `frontend/src/engine/race/hooks/useRaceEngine.ts`.
- [X] T038 [US3] Apply Tier 3 multiplication, Tier 4 division, and parent-configured Tier 6 settings in `backend/app/mathematics/tiers.py`, `frontend/src/engine/math/tiers.ts`, `frontend/src/engine/math/generator.ts`, and `frontend/src/pages/RaceSetupPage.tsx`.
- [X] T039 [US3] Remove client authority over XP and display server-confirmed Training and championship rewards in `frontend/src/features/race/progressionApi.ts` and `frontend/src/pages/ResultsScreenPage.tsx`.
- [X] T040 [US3] Run progression, race-engine, mathematics, and relevant page tests and record D-04, D-10, and D-12 evidence.

## Phase 6: User Story 4 - See accurate learning progress (Priority: P1)

**Goal**: Derive operation summaries from saved child answers and ensure
released achievements have tested, idempotent triggers.

**Independent Test**: Save answers from multiple operations, compare all three
operation summaries with the answers, and deliver each supported achievement
event more than once.

- [X] T041 [P] [US4] Add failing tests for strongest, weakest, favourite operations, ties, and no-answer states in `backend/tests/unit/statistics/test_domain_service.py`.
- [X] T042 [P] [US4] Add failing trigger and duplicate-event tests for each released achievement in `backend/tests/unit/achievements/test_domain_service.py`.
- [X] T043 [US4] Implement deterministic operation summaries from child-owned answers in `backend/app/statistics/domain_service.py`, `backend/app/statistics/repository.py`, and `backend/app/statistics/schemas.py`.
- [X] T044 [US4] Implement and test the released achievement catalogue, event predicates, and unique child unlocks in `backend/app/achievements/catalogue.py`, `backend/app/achievements/domain_service.py`, and `backend/app/achievements/repository.py`.
- [X] T045 [US4] Display the server-derived operation summaries in `frontend/src/features/statistics/statisticsApi.ts`, `frontend/src/pages/StatisticsPage.tsx`, and `frontend/src/pages/StatisticsPage.test.tsx`.
- [X] T046 [US4] Run statistics and achievement tests and record D-05 and D-06 evidence.

## Phase 7: User Story 5 - Use safe avatar generation (Priority: P1)

**Goal**: Block unsafe or unchecked images, apply API security controls, make
providers replaceable, and keep route handlers thin.

**Independent Test**: Exercise API state changes without valid CSRF, exceed
rate limits, replace provider fakes, and make each required image check fail or
unavailable. No blocked image can be read by a child.

- [X] T047 [P] [US5] Add failing API tests for CSRF, origin checks, login/registration limits, and generation limits in `backend/tests/integration/test_api_security.py`.
- [X] T048 [P] [US5] Add failing image-safety tests for unsafe, invalid, and unavailable check results in `backend/tests/unit/avatars/test_generation_service.py`.
- [X] T049 [US5] Implement shared CSRF token and origin validation for state-changing requests in `backend/app/presentation/api/middleware/csrf.py` and `backend/app/main.py`.
- [X] T050 [US5] Implement Redis-backed login and registration limits and verify documented avatar limits in `backend/app/presentation/api/v1/auth.py`, `backend/app/avatars/domain_service.py`, and `backend/infrastructure/`.
- [X] T051 [US5] Define AI generation and object-storage interfaces in `backend/infrastructure/` and inject them into `backend/app/avatars/generation_service.py`.
- [X] T052 [US5] Use the approved GPT Image provider through the AI interface in `backend/infrastructure/`.
- [X] T053 [US5] Add blocking technical and child-safety checks before persistence or publication in `backend/app/avatars/generation_service.py` and `backend/app/avatars/models.py`.
- [X] T054 [US5] Move child-profile and cross-domain rules from route handlers into application/domain services in `backend/app/child_profiles/presentation/api/v1/child_profiles.py`, `backend/app/races/presentation/api/v1/races.py`, and `backend/application/`.
- [X] T055 [US5] Run API-boundary security, image-safety, adapter, and route tests and record D-07, D-08, D-11, and D-14 evidence.

## Phase 8: User Story 6 - Practise with cached data while offline (Priority: P2)

**Goal**: Allow cached-child Training offline and sync each queued result once
without losing it when the connection or server fails.

**Independent Test**: Cache the selected child's required data, disconnect,
complete Training, reconnect, and verify one saved result and reward.

- [X] T056 [P] [US6] Add failing tests for offline avatar access, queued results, retry, and duplicate sync in `frontend/src/infrastructure/offline/offlineStore.test.ts` and `frontend/src/pages/RaceSetupPage.test.tsx`.
- [X] T057 [US6] Implement typed IndexedDB storage for child avatar/statistics cache and pending results in `frontend/src/infrastructure/offline/offlineStore.ts`.
- [X] T058 [US6] Cache selected-child data and open Training without a network request in `frontend/src/pages/RaceSetupPage.tsx` and `frontend/src/infrastructure/offline/`.
- [X] T059 [US6] Queue completed Training results with stable idempotency keys and retain them until server confirmation in `frontend/src/features/race/` and `frontend/src/infrastructure/offline/`.
- [X] T060 [US6] Add network restoration sync and visible retry/error state in `frontend/src/infrastructure/offline/` and `frontend/src/pages/`.
- [X] T061 [US6] Run offline store, race setup, Training, and result API tests and record D-09 and D-13 evidence.

## Phase 9: Polish and cross-cutting acceptance

**Purpose**: Prove all audit findings are addressed and report any environment
checks that cannot be completed.

- [X] T062 [P] Review all published API and product documents against implemented behaviour in `docs/`, `initial_spec/`, and `specs/014-audit-remediation/`.
- [ ] T063 Run migration upgrade, downgrade, and restore checks with representative legacy data using the repository-supported database process; record results in `specs/014-audit-remediation/quickstart.md`.
- [ ] T064 Measure startup, race loading, problem generation, and frame rate in the target test environment; record evidence and blockers in `specs/014-audit-remediation/quickstart.md`.
- [ ] T065 Run keyboard, screen-reader, contrast, reduced-motion, and supported-browser checks on changed screens; record evidence and blockers in `specs/014-audit-remediation/quickstart.md`.
- [X] T066 Run relevant backend and frontend tests, then `make ci`; fix failures caused by this work and record exact results in `specs/014-audit-remediation/quickstart.md`.
- [X] T067 Check D-01 through D-14 against their acceptance evidence and update `audit/discrepancies.md` without marking unverified items complete.
- [ ] T068 Review the full diff, run `git diff --check`, and prepare the implementation pull request to `main` only after validation is complete.

## Dependencies and execution order

- Phase 1 must finish before application behaviour changes.
- Phase 2 is a prerequisite for User Stories 1 through 6 because every new
  record and query needs a validated child owner.
- User Story 1 must finish before dependent Training and offline result sync
  work. User Story 2 ownership work must finish before child-scoped summaries,
  avatar safety publication, and offline cache work.
- User Stories 3 and 4 depend on the race result use case and saved operation
  answers. Championship and achievement rewards use the same transaction.
- User Story 5 security boundaries apply to all state-changing endpoints.
- User Story 6 depends on the session/result contract and stable idempotency
  keys from User Story 1.
- Phase 9 depends on all implementation stories and their focused tests.

## Parallel opportunities

- T002, T003, and T004 can proceed in parallel after T001, if edits do not
  overlap.
- T008 and T009 can proceed in parallel.
- T014 and T015 can proceed in parallel.
- T024 and T025 can proceed in parallel.
- T033 and T034 can proceed in parallel.
- T041 and T042 can proceed in parallel.
- T047 and T048 can proceed in parallel.
- T056 can start after the race result contract is stable.

## Implementation strategy

1. Complete the approved requirement updates and migration foundation.
2. Implement and independently verify race sessions, human identity, atomic
   result handling, and child ownership.
3. Add the approved game rules, statistics, and achievement triggers.
4. Add security, safe generation, service adapters, and offline Training.
5. Run cross-cutting acceptance and operational checks. Report unresolved
   environment work as blocked. Do not merge the implementation branch.
