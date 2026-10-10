# Tasks: UI Localization

**Input**: Design documents from `/specs/015-ui-localization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Phase 1: Setup

**Purpose**: Establish the shared, typed localization module.

- [x] T001 Create supported-locale types, three catalog structures, and the translation context in `frontend/src/infrastructure/localization/catalogs.ts` and `frontend/src/infrastructure/localization/LocaleContext.tsx`

## Phase 2: Foundational

**Purpose**: Make locale state available to every route before adding user-facing flows.

- [x] T002 Provide the localization context around the router and authentication providers in `frontend/src/main.tsx`

## Phase 3: User Story 1 - Change the interface language anywhere (Priority: P1) 🎯 MVP

**Goal**: Let users change the active interface language from every route without reloading or losing in-progress state.

**Independent Test**: On login, an authenticated screen, and an active race, change the locale and verify immediate translated updates with no route change, input loss, or race restart.

### Tests for User Story 1

- [x] T003 [P] [US1] Test selector options, keyboard selection, and locale change behavior in `frontend/src/shared/components/LanguageSwitcher.test.tsx`
- [x] T004 [P] [US1] Test that the app shell keeps the selector mounted while route content changes in `frontend/src/App.test.tsx`

### Implementation for User Story 1

- [x] T005 [US1] Implement an accessible, always-visible language selector in `frontend/src/shared/components/LanguageSwitcher.tsx`
- [x] T006 [US1] Render the selector beside the route outlet without remounting route content in `frontend/src/App.tsx`

## Phase 4: User Story 2 - Use the selected language throughout a session (Priority: P1)

**Goal**: Detect a supported browser language on first use, preserve explicit choices across routes and reloads, and expose the current document language.

**Independent Test**: Verify browser-language selection and fallback with no saved value, then choose each language and verify it persists through navigation and reload.

### Tests for User Story 2

- [x] T007 [P] [US2] Test stored preference precedence, browser locale normalization, unsupported-locale fallback, and document `lang` updates in `frontend/src/infrastructure/localization/LocaleContext.test.tsx`

### Implementation for User Story 2

- [x] T008 [US2] Implement browser locale resolution, explicit preference persistence, and root document language updates in `frontend/src/infrastructure/localization/LocaleContext.tsx`

## Phase 5: User Story 3 - Read all application-provided interface text (Priority: P1)

**Goal**: Translate every application-authored interface message, including visible content, errors, dynamic labels, and accessibility text, into all three supported languages.

**Independent Test**: Visit every route and state in each locale and verify no application-authored string is untranslated or missing; verify all catalogs share the same key set.

### Tests for User Story 3

- [x] T009 [P] [US3] Test that Russian, English, and Spanish catalogs contain the same non-empty message keys in `frontend/src/infrastructure/localization/catalogs.test.ts`

### Implementation for User Story 3

- [x] T010 [US3] Add complete translated messages and typed interpolation values for all product UI copy in `frontend/src/infrastructure/localization/catalogs.ts`
- [x] T011 [US3] Localize shared controls, notifications, avatar-card actions, and achievement toast text in `frontend/src/shared/components/ConfirmDialog.tsx`, `frontend/src/shared/components/ErrorState.tsx`, `frontend/src/shared/components/LoadingSpinner.tsx`, `frontend/src/shared/components/NotificationToast.tsx`, `frontend/src/shared/components/XPBar.tsx`, `frontend/src/features/avatar/AvatarCard.tsx`, and `frontend/src/components/achievements/AchievementToast.tsx`
- [x] T012 [US3] Localize authentication, child-profile, home, and settings copy and validation in `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx`, `frontend/src/pages/ChildProfileSelectPage.tsx`, `frontend/src/pages/HomePage.tsx`, `frontend/src/pages/SettingsPage.tsx`, and `frontend/src/infrastructure/localization/authErrors.ts`
- [x] T013 [US3] Localize avatar creation/gallery and race setup/active-game copy, dynamic instructions, and accessible names in `frontend/src/pages/AvatarCreatorPage.tsx`, `frontend/src/pages/AvatarGalleryPage.tsx`, `frontend/src/pages/RaceSetupPage.tsx`, `frontend/src/pages/RaceScreenPage.tsx`, and `frontend/src/features/avatar/useAvatarGallery.ts`
- [x] T014 [US3] Localize results, championship, statistics, and parent-dashboard messages and accessible names in `frontend/src/pages/ResultsScreenPage.tsx`, `frontend/src/pages/ChampionshipPage.tsx`, `frontend/src/pages/StatisticsPage.tsx`, and `frontend/src/pages/ParentDashboardPage.tsx`
- [x] T015 [US3] Audit all runtime frontend source for remaining application-authored user-facing literals, localize any remaining text, and update affected component and page tests under `frontend/src/`

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep product documentation aligned and verify the complete feature.

- [x] T016 [P] Update the screen inventory and UI implementation specification for the global language selector in `docs/ui/screens.md` and `docs/ui/spec-ui-implementation.md`
- [x] T017 Run localization acceptance checks, the full frontend test suite, lint, type-check, and production build using `specs/015-ui-localization/quickstart.md`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on setup; makes locale context available to all routes.
- **User Stories (Phases 3-5)**: Depend on the foundational provider.
- **Polish (Phase 6)**: Depends on all three user stories.

### User Story Dependencies

- **US1**: Depends on the shared locale context; delivers the global language control.
- **US2**: Depends on US1's locale selection; adds first-visit resolution and persistence.
- **US3**: Depends on US1 and US2; replaces existing UI text with complete translations.

### Parallel Opportunities

- T003 and T004 can be authored in parallel because they cover separate test files.
- T007 and T009 can be authored in parallel because they cover separate tests.
- Documentation task T016 can be completed independently of UI source localization.
- Most UI groups in T011-T014 touch separate source files, but all add keys to the shared catalogs; catalog edits must be coordinated to avoid conflicts.

## Implementation Strategy

1. Complete setup and provider wiring.
2. Deliver US1 as the MVP: a visible selector that changes locale immediately on every route.
3. Complete US2: browser-language initialization, explicit-choice persistence, and document-language accessibility.
4. Complete US3: populate complete catalogs, migrate all application-authored text, and update affected tests.
5. Update UI documentation and run every check listed in the quickstart.

## Notes

- `[P]` marks tasks that can be performed independently without editing the same files.
- User-authored names and other user-provided content remain unchanged.
- There is no backend, database, or API contract change.
