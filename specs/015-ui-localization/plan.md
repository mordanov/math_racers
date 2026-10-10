# Implementation Plan: UI Localization

**Branch**: `015-ui-localization` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/015-ui-localization/spec.md`

## Summary

Add Russian, English, and Spanish localization to every application-authored frontend message. A persistent app-shell language selector will switch the current screen immediately, preserve in-progress UI state, and save the preference. A small typed React context and shared message-key catalog avoid a new runtime dependency while TypeScript and tests enforce complete translations.

## Technical Context

**Language/Version**: TypeScript 5.4, React 18
**Primary Dependencies**: Existing React, React Router, Vite, and Vitest stack; no new runtime dependency
**Storage**: Browser `localStorage` for the explicit language preference
**Testing**: Vitest, Testing Library, TypeScript strict type-check, frontend build
**Target Platform**: Existing desktop and tablet web browsers
**Project Type**: React single-page application
**Performance Goals**: Language changes update the current UI without a page reload or perceptible delay
**Constraints**: Three complete catalogs; persistence must be local to the browser; all routes share one persistent selector; preserve forms and active race state
**Scale/Scope**: All application-owned user-facing text in app pages, shared components, feature components, notifications, accessible names, validation and API error feedback

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| IV. Architecture | PASS | Keep localization in frontend infrastructure/shared UI; no backend or domain changes. |
| V. Documentation First | PASS | Update the authoritative UI screen and implementation specifications with global selector behavior. |
| VI. Simplicity | PASS | Use a typed in-app catalog and React context for the fixed three-language scope; do not add an i18n dependency solely for basic lookups. |
| VIII. Consistency | PASS | Follow existing feature-sliced frontend and co-located Vitest conventions. |
| X. Frontend Principles | PASS | Keep locale state and rendering in frontend infrastructure; keep feature/domain behavior unchanged. |
| XVII. Accessibility | PASS | Keyboard-operable selector, translated accessible text, and synchronized document language. |
| XVIII. Testing | PASS | Test immediate switching, persistence/fallback, complete key parity, and representative routes/states. |
| XIX. Dependencies | PASS | No new dependency; native browser APIs cover locale selection, persistence, and document language. |
| XX. Documentation Maintenance | PASS | Update the two authoritative UI documents alongside implementation. |

**Gate result**: PASS. No constitution violations or unresolved design questions.

## Phase 0: Research

### Decision: Use a typed React localization context

- Keep three in-bundle catalogs keyed by one shared TypeScript message-key type.
- Initialize with a valid saved choice first; otherwise normalize the browser's preferred language to `ru`, `en`, or `es`, falling back to Russian.
- Persist only an explicit user selection in `localStorage`.
- Set the root document's `lang` attribute whenever the active locale changes.
- Use a recursive or flat catalog parity test and TypeScript `Record` types so any missing locale key fails verification.

**Rationale**: The current frontend has three fixed locales and no existing localization framework. A typed context supports immediate React updates, interpolation where needed, local persistence, browser-language fallback, and compile-time completeness without adding a framework or detector dependency.

**Alternatives considered**:

- `i18next` + `react-i18next` + browser language detector: mature and feature-rich, but adds runtime packages and configuration for capabilities not required by this fixed, in-bundle use case.
- Raw string constants in components: rejected because it cannot switch languages or verify complete coverage.

**Reference material**:

- `navigator.language` provides the browser's preferred language: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language
- The HTML `lang` global attribute communicates document language to browsers and assistive technologies: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/lang
- React context is appropriate for state shared across the route tree; keep state changes at the app shell so route components rerender without remounting.

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md). This is client-only state; no backend persistence or account changes are required.

### Contracts

No external API or backend contract is introduced. Locale selection is an in-app user preference.

### Quickstart

See [quickstart.md](quickstart.md) for automated and manual acceptance checks.

### Project Structure

```text
frontend/src/
├── App.tsx                         # Persistent selector and route outlet
├── infrastructure/
│   └── localization/
│       ├── LocaleContext.tsx        # Locale state, persistence, translation hook
│       ├── catalogs.ts              # Typed English, Russian, Spanish message catalogs
│       └── LocaleContext.test.tsx   # Selection, fallback, persistence, coverage tests
├── shared/components/
│   └── LanguageSwitcher.tsx         # Always-visible accessible control
├── pages/                           # Replace all page UI literals with message keys
├── features/                        # Replace user-facing feature/component literals
└── components/                      # Replace remaining application-authored UI literals

docs/ui/
├── screens.md                       # Global language availability
└── spec-ui-implementation.md        # Persistent app-shell behavior
```

**Structure Decision**: Extend the existing React SPA. Keep locale data and state in frontend infrastructure, the selector in shared UI, and use the existing App route shell so authentication, gameplay, and all authenticated routes inherit it.

## Phase 1 Constitution Re-check

PASS. The design keeps locale behavior client-side, adds no service or data migration, uses no new dependency, preserves route state, and includes accessibility and translation-completeness checks.

## Complexity Tracking

No constitution violations.
