# Feature Specification: UI Localization

**Feature Branch**: `015-ui-localization`
**Created**: 2026-10-10
**Status**: Draft
**Input**: User description: "Для UI приложения нужен переключатель языков Русский/Английский/Испанский. Этот переключатель должен быть доступен всегда из любого места UI. Перевод должен содержать все строки текста - используй i18next или по твоему выбору."

## User Scenarios & Testing

### User Story 1 - Change the interface language anywhere (Priority: P1)

A child or parent can choose Russian, English, or Spanish from a language control that remains available throughout the application, including authentication screens and an active race. The current screen updates immediately without losing progress or requiring a reload.

**Why this priority**: Users need to understand and operate every part of the game in their chosen language.

**Independent Test**: Open each route and an active race, change the language, and verify that the current view changes language without navigation or lost state.

**Acceptance Scenarios**:

1. **Given** a user is on any application screen, **When** they choose another supported language, **Then** all interface text on that screen changes immediately and the current route and entered data remain intact.
2. **Given** a race is in progress, **When** the user changes the language, **Then** gameplay continues and all interface labels, prompts, and controls use the selected language.
3. **Given** a user is on login or registration, **When** they change the language, **Then** the authentication form and its validation and error messages use the selected language.

### User Story 2 - Use the selected language throughout a session (Priority: P1)

A user can move between public, parent, child, and gameplay screens without the language reverting.

**Why this priority**: A globally available control is not useful if navigation changes the chosen language.

**Independent Test**: Select a language, navigate through the main flows, and verify that all destination screens keep that language.

**Acceptance Scenarios**:

1. **Given** a language has been selected, **When** a user navigates to another route, **Then** the destination screen is rendered in the same language.
2. **Given** a language has been selected, **When** the user reloads the application, **Then** the selection is restored.
3. **Given** a stored language preference is missing or unsupported, **When** the application starts, **Then** it uses the browser's supported language when available and otherwise uses Russian.

### User Story 3 - Read all application-provided interface text (Priority: P1)

Children and parents see complete, consistent translations for all application-authored interface text, not only primary page headings.

**Why this priority**: Mixed-language screens make the application difficult to understand and can hide important errors or instructions.

**Independent Test**: Visit every route and state in each supported language and confirm all application-authored visible text and accessibility labels are localized, with no missing-key or untranslated fallback text.

**Acceptance Scenarios**:

1. **Given** any supported language is selected, **When** any route, dialog, toast, loading state, empty state, validation error, or API error is shown, **Then** all application-authored text is displayed in that language.
2. **Given** a screen contains controls usable by assistive technology, **When** the selected language changes, **Then** accessible names, descriptions, and announcements change to that language as well.
3. **Given** the user switches languages repeatedly, **When** each screen is inspected, **Then** no translation key, raw localization identifier, or missing-language placeholder is visible.

## Edge Cases

- The browser reports an unsupported language and the user has no saved preference.
- A previously saved language value is invalid or no longer supported.
- A translation is absent during development or a dynamic error code is unknown.
- The selected language changes while a modal, toast, validation message, or race countdown is active.
- A language switch occurs while offline or while a request is in progress.
- User-provided names and other user-authored content contain words in a language different from the interface.

## Requirements

### Functional Requirements

- **FR-001**: The application MUST offer Russian, English, and Spanish as selectable interface languages.
- **FR-002**: A language selector MUST remain available on every application route and in all application states, including login, registration, parent and child views, dialogs, and active gameplay.
- **FR-003**: Selecting a language MUST update the current screen immediately without a full page reload, route change, form reset, or interruption of an active race.
- **FR-004**: The selected language MUST remain consistent across routes and MUST be restored after the application is reloaded.
- **FR-005**: On a first visit without a saved selection, the application MUST use the browser's language when it matches a supported language and MUST otherwise use Russian.
- **FR-006**: Every application-authored user-facing string MUST have complete Russian, English, and Spanish translations. This includes headings, labels, buttons, help text, placeholders, validation and API errors, notifications, dialogs, loading and empty states, game instructions and status labels, and accessibility text.
- **FR-007**: All supported translations MUST cover the same set of required interface messages; a missing translation MUST be detected during development or verification rather than silently shown to users.
- **FR-008**: The language selector and all translated interactive controls MUST remain keyboard-operable and expose accessible names in the current language.
- **FR-009**: Changing the interface language MUST NOT translate user-authored profile names or other user-provided content.
- **FR-010**: The application MUST expose the selected language to browser and assistive-technology language handling.

### Key Entities

- **Supported language**: One of Russian, English, or Spanish, with its user-facing name and complete set of interface messages.
- **Language preference**: The language currently selected by the user and restored when the application is revisited.
- **Interface message**: An application-authored user-facing string with equivalent translations for all supported languages.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can switch among all three languages from every route without reloading or losing current navigation, form, or race state.
- **SC-002**: 100% of application-authored interface messages used by the application have Russian, English, and Spanish translations.
- **SC-003**: A chosen language remains active across all routes and is restored after a page reload.
- **SC-004**: No supported-language screen exposes raw translation keys, missing-message placeholders, or application-authored text in another language.
- **SC-005**: Keyboard and assistive-technology users can identify and operate the language selector in every application state.

## Assumptions

- The browser's preferred language is used only when no explicit saved selection exists; unsupported browser languages fall back to Russian.
- The preference is local to the browser and is not synchronized across accounts or devices.
- Application-authored text is translated; user-authored names and content remain unchanged.
- The language selector is part of the persistent application shell and stays visible during gameplay rather than being limited to Settings.

## Acceptance Criteria

- [ ] Russian, English, and Spanish are available in the global language selector on every route.
- [ ] Switching languages updates all application-authored screen and accessibility text immediately without losing state.
- [ ] Every application-authored UI message has equivalent text in all three languages.
- [ ] The explicit selection persists across routes and reloads; an unsupported browser language falls back to Russian when there is no saved selection.
- [ ] The selected language is exposed through the document language and the selector is keyboard accessible.

## Manual Verification

1. Clear the saved language preference and open the application with a Russian, English, Spanish, and unsupported browser locale; verify the expected initial language in each case.
2. On login and registration, use the language selector and check labels, placeholders, validation feedback, and API errors in each language.
3. Sign in and navigate through child selection, home, avatar creation/gallery, race setup, an active race, results, championship, statistics, settings, and parent dashboard; verify the selector stays available and each screen is fully translated.
4. Change language during an active race and while a dialog or toast is visible; verify the race and current interaction continue without navigation or lost input.
5. Reload after selecting each language and verify that the choice is restored.
6. Use only the keyboard and a screen reader to locate and operate the language selector on both an authentication screen and an authenticated gameplay screen.
