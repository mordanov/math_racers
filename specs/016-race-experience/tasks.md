# Tasks: Race Experience Improvements

**Input**: Design documents from `specs/016-race-experience/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/math-generation.md`, `contracts/race-and-championship.md`

**Organization**: Tasks are grouped by the feature's five user stories. Automated
regression tests are required by the project Constitution; implement each
behavior only after adding its focused test.

## Phase 1: Setup (Documentation First)

**Purpose**: Update authoritative gameplay documentation before changing code.

- [X] T001 Update `initial_spec/gdd.md`, `docs/gameplay/feature-math-engine.md`, `docs/gameplay/spec-math-engine.md`, `docs/gameplay/feature-race-engine.md`, `docs/gameplay/spec-race-engine.md`, `docs/gameplay/feature-game-modes.md`, `docs/gameplay/spec-game-modes.md`, `docs/ui/spec-ui-implementation.md`, and `docs/engineering/audio-design.md` with the approved timer, math, timeout, championship, avatar, and audio behavior.

## Phase 2: Foundational

**Purpose**: No database migration is needed. T001 is the blocking
documentation prerequisite for every user story; the shared avatar catalog is
implemented as an isolated authenticated API addition in US4.

## Phase 3: User Story 1 - Give the child enough time to calculate (Priority: P1)

**Goal**: Parents can set a 10–60 second limit per competitive problem (default
30), timeout answers are saved once, and Training stays untimed.

**Independent Test**: Select a duration, start a race, change the preference
mid-race, and verify the active race is unchanged; let one problem expire and
confirm the ordered blank answer is persisted once with zero movement. Verify
Training has no timeout.

- [X] T002 [P] [US1] Add Settings timer range, default, and persistence tests in `frontend/src/pages/SettingsPage.test.tsx`.
- [X] T003 [P] [US1] Add active-race snapshot, timeout-once (including expiry during answer submission), no-movement, and Training exemption tests in `frontend/src/pages/RaceScreenPage.test.tsx`; add hidden-tab pause/resume coverage in `frontend/src/engine/race/hooks/useRaceEngine.test.ts`.
- [X] T004 [P] [US1] Add ordered empty-answer persistence and identical-retry coverage in `backend/tests/integration/races/test_api_races.py`.
- [X] T005 [P] [US1] Add localized timer-setting labels and duration choices to `frontend/src/infrastructure/localization/catalogs.ts`.
- [X] T006 [US1] Add validated 10–60 second, 5-second-step preference control with a 30-second default in `frontend/src/pages/SettingsPage.tsx`.
- [X] T007 [US1] Read and snapshot the selected duration for competitive race setup in `frontend/src/pages/RaceSetupPage.tsx` and `frontend/src/pages/RaceScreenPage.tsx`.
- [X] T008 [US1] Enforce the snapshot duration, pause/resume it with the race clock, submit one blank answer at expiry (without racing an in-flight answer), advance after its response, and preserve untimed Training behavior in `frontend/src/pages/RaceScreenPage.tsx` and `frontend/src/engine/race/raceEngine.ts`.

## Phase 4: User Story 2 - Practice appropriately challenging arithmetic (Priority: P1)

**Goal**: Tiers 3–5 use the specified operand widths and division never
generates a self-division problem; both seeded generators stay aligned.

**Independent Test**: Generate 1,000 seeded problems per tier in both
implementations and verify operation constraints, exact division, deterministic
order, and no self-division.

- [X] T009 [P] [US2] Add seeded tier 3–6 operand and no-self-division tests in `frontend/src/engine/math/generator.test.ts` and invalid Tier 6 settings coverage in `frontend/src/pages/RaceSetupPage.test.tsx`.
- [X] T010 [P] [US2] Add matching seeded division tests in `backend/tests/unit/mathematics/test_generator.py`, Tier 6 validation cases in `backend/tests/unit/mathematics/test_difficulty.py`, and cross-language parity coverage in `backend/tests/unit/mathematics/test_rng_parity.py`.
- [X] T011 [US2] Implement operation-specific tier 3–5 operand selection, quotient-greater-than-one Tier 6 division, and invalid-range validation in `frontend/src/engine/math/generator.ts`, `frontend/src/engine/math/tiers.ts`, and `frontend/src/pages/RaceSetupPage.tsx`.
- [X] T012 [US2] Mirror tier 3–5 operand rules, quotient-greater-than-one Tier 6 division, and validation for saved and race-session settings in `backend/app/mathematics/generator.py`, `backend/app/mathematics/tiers.py`, `backend/app/mathematics/schemas.py`, and `backend/app/races/schemas.py`.

## Phase 5: User Story 3 - Complete a championship and keep its results (Priority: P1)

**Goal**: Championship races reliably persist race results, standings,
continuation state, and completion without double-counting retries.

**Independent Test**: Complete and reload between races in a championship;
verify each race advances standings once and the final race persists completion.

- [X] T013 [US3] Reproduce the reported result-save failure with a regression test for the ordered result/championship request flow in `frontend/src/pages/ResultsScreenPage.test.tsx` and `backend/tests/integration/championships/test_api_championships.py`.
- [X] T014 [US3] Trace and fix the reproduced failing result-save or retry transition in the applicable files among `frontend/src/pages/ResultsScreenPage.tsx`, `frontend/src/engine/race/championshipApi.ts`, `backend/app/races/domain_service.py`, `backend/app/championships/domain_service.py`, and their repositories.
- [X] T015 [US3] Verify retry idempotency, standings persistence, resume, and final completion with regression coverage in `frontend/src/pages/ResultsScreenPage.test.tsx`, `backend/tests/integration/championships/test_api_championships.py`, and `backend/tests/unit/championships/test_domain_service.py`.

## Phase 6: User Story 4 - See their avatar racing (Priority: P2)

**Goal**: Show participant portraits on the track, move them with existing race
progress, and preserve accessibility and fallback behavior.

**Independent Test**: Start races with available and unavailable portraits,
change progress, and enable reduced motion; verify imagery/fallbacks move with
the racers and motion preference is respected.

- [X] T016 [US4] Add portrait movement, missing-image fallback, and reduced-motion tests in `frontend/src/pages/RaceScreenPage.test.tsx`.
- [X] T017 [US4] Pass the selected player portrait and portraits from the shared published-avatar catalog (never private child-profile portraits) from `frontend/src/pages/RaceSetupPage.tsx` into the race configuration; render accessible moving racer images with a distinct fallback in `frontend/src/pages/RaceScreenPage.tsx`. Depends on T025.
- [X] T024 [P] [US4] Add catalog endpoint coverage verifying authentication, published-avatar filtering, active-portrait filtering, and that only portrait URLs are returned in `backend/tests/integration/avatars/test_api_avatars.py`.
- [X] T025 [US4] Add an authenticated app-wide published-avatar catalog that returns only active portrait URLs in `backend/app/avatars/repository.py`, `backend/app/avatars/domain_service.py`, `backend/app/avatars/schemas.py`, and `backend/app/avatars/presentation/api/v1/avatars.py`; add the frontend client method and response type in `frontend/src/engine/avatar/avatarApi.ts` and `frontend/src/engine/avatar/types.ts`. Depends on T024.

## Phase 7: User Story 5 - Adjust music and sound effects separately (Priority: P2)

**Goal**: Existing music and SFX settings apply immediately and independently,
including to active music, and persisted values/defaults are consistent.

**Independent Test**: Adjust music while it is playing and SFX while triggering
an effect; verify immediate independent changes and persistence after reload.

- [X] T018 [P] [US5] Add same-page music-volume update and default-value tests in `frontend/src/shared/hooks/useAudioManager.test.ts`.
- [X] T019 [US5] Notify the active music manager when `settings.musicVolume` changes and align audio-hook fallback values with Settings defaults in `frontend/src/pages/SettingsPage.tsx`, `frontend/src/shared/hooks/useAudioManager.ts`, and `frontend/src/shared/hooks/useSfxPlayer.ts`.
- [X] T020 [US5] Verify music and SFX sliders remain independent, accessible, and persistent in `frontend/src/pages/SettingsPage.test.tsx` and `frontend/src/shared/hooks/useSfxPlayer.test.ts`.

## Phase 8: Polish and Cross-Cutting Concerns

**Purpose**: Keep implementation documentation and the repository knowledge
graph current, then run focused verification.

- [X] T021 [P] Update implemented behavior and manual verification steps in `specs/016-race-experience/spec.md`, `specs/016-race-experience/data-model.md`, `specs/016-race-experience/contracts/math-generation.md`, `specs/016-race-experience/contracts/race-and-championship.md`, and `specs/016-race-experience/quickstart.md`.
- [X] T022 Run the focused frontend and backend commands in `specs/016-race-experience/quickstart.md` and resolve failures.
- [X] T023 Run `graphify update .` after code changes and verify the updated graph is generated.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 must finish before any code task because gameplay
  documentation is authoritative.
- **Foundational (Phase 2)**: No separate infrastructure, migration, or API
  work is required; the setup documentation is the shared prerequisite.
- **User Stories (Phases 3–7)**: Each story can be implemented independently
  after T001. User Stories 1–3 are P1; User Stories 4–5 are P2.
- **Polish (Phase 8)**: Requires all selected story work to be complete.

### User Story Dependencies

- **US1 (P1)**: Depends on T001 only; uses the existing ordered answer API.
- **US2 (P1)**: Depends on T001 only; frontend and backend generator changes
  must use matching rules.
- **US3 (P1)**: Depends on T001 only; preserve existing persisted race and
  championship semantics.
- **US4 (P2)**: Depends on T001; T025 follows its endpoint regression test T024,
  and frontend integration T017 follows T025.
- **US5 (P2)**: Depends on T001 only; reuses existing browser preference keys.

### Parallel Opportunities

- T002–T005 can be developed independently because they touch separate test or
  localization files.
- T009 and T010 can be developed independently; T011 and T012 can proceed in
  parallel after their corresponding failing tests are added.
- After T001, the five user stories are independently testable, though US1 and
  US4 both touch `RaceScreenPage.tsx` and should not edit that file concurrently.
- T018 can run independently of the UI verification work in T020.

## Parallel Example: User Story 2

```text
Task: T009 frontend tier 3–6 generator and Tier 6 settings tests
Task: T010 backend generator, settings validation, and parity tests
```

After both test tasks are in place, implement TypeScript and Python generator
and validation changes in parallel as T011 and T012.

## Implementation Strategy

1. Complete T001 before any application code.
2. Deliver US1, US2, and US3 as the P1 increment; verify each independently.
3. Deliver US4 and US5 as separate P2 increments.
4. Complete T021–T023 after feature work, then review the full diff before
   committing or opening a PR.
