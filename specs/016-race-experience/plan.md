# Implementation Plan: Race Experience Improvements

**Branch**: `016-race-experience` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/016-race-experience/spec.md`

## Summary

Improve the pacing and readability of timed races, constrain tiers 3–5 to
mental-arithmetic operand ranges, and exclude self-division. Reproduce and fix
the race-results-to-championship handoff. Render racers as avatar portraits and
ensure the existing independent audio controls immediately affect playback.
Reuse existing frontend race simulation, answer/result APIs, settings storage,
and domain modules; add no service, dependency, or database migration.

## Technical Context

**Language/Version**: Python >=3.12; TypeScript >=5.4  
**Primary Dependencies**: FastAPI, SQLAlchemy async, React 18, React Router, Vitest; no new dependencies  
**Storage**: PostgreSQL for existing race/championship results; browser localStorage for device-level race timing and audio preferences  
**Testing**: pytest unit/integration tests; Vitest and Testing Library; frontend lint/type-check/build  
**Target Platform**: Docker Compose backend and supported desktop/tablet browsers  
**Project Type**: Web application and API; modular monolith  
**Performance Goals**: Keep race rendering responsive; preserve deterministic generated problem order; timer precision remains on the existing monotonic game clock  
**Constraints**: Backend remains authoritative for persisted answers/results; frontend owns race simulation and presentation; Training remains unlimited and untimed; no new database schema or runtime dependency  
**Scale/Scope**: Existing math, race, championship, settings/audio, and avatar-rendering modules across frontend and backend

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| IV. Architecture | PASS | Reuse existing modular monolith and domain/repository layering; no new service. |
| V. Documentation First | PASS | Update source GDD and affected gameplay/UI/audio specifications before code. |
| VI. Simplicity | PASS | Keep preferences in existing browser settings; add no library, service, or migration. |
| VII–VIII. Code Quality and Consistency | PASS | Mirror seeded math rules in existing Python and TypeScript generators and co-located tests. |
| IX–X. Backend and Frontend Principles | PASS | Backend persists/validates answers and results; frontend owns timer display, simulation, and avatar movement. |
| XI. Gameplay | PASS | Encode the approved 30-second default, per-problem timing, and operand constraints in source documentation first. Preserve Training's untimed mode. |
| XIV–XV. Data Ownership and Security | PASS | Use existing authenticated race and championship APIs; no child data is reassigned or exposed. |
| XVII–XVIII. Accessibility and Testing | PASS | Respect reduced motion, accessible labels, and focused frontend/backend regression coverage. |
| XX–XXI. Documentation and Observability | PASS | Document timeout and persistence behavior; retain actionable result-save errors and retry behavior. |

**Gate result**: PASS. No architecture or data migration is required.

## Design Decisions

1. Store the 10–60 second (5-second step) per-problem preference in the
   existing browser settings, defaulting to 30 seconds. Snapshot it when a
   timed race starts; do not time Training. Pause/resume it with the existing
   race clock when the browser tab loses/gains focus.
2. On expiry, submit an empty answer through the existing ordered answer
   endpoint. The server records it as incorrect; the race engine awards zero
   movement and advances. Guard against duplicate timeout submissions.
3. Keep TypeScript and Python generation deterministic and aligned. For tiers
   3–5, apply operation-specific operand ranges while preserving Tier 6's
   parent-selected operations/ranges. All division uses a quotient of at least
   two; reject Tier 6 division ranges that cannot produce such a problem.
4. Trace the actual Results → race result → championship result flow before
   changing it. Preserve idempotency, authoritative positions, and the existing
   championship completion/XP transaction.
5. The existing Settings page already has separate music and SFX sliders.
   Reuse them and make their values consistent with defaults and immediately
   effective for active playback; do not add duplicate controls.
6. Render each track lane with the selected player portrait and portraits from
   the shared published-avatar catalog for opponents, using a distinct safe
   fallback when one is unavailable. Never expose private child-profile
   portraits. Preserve reduced-motion behavior.
   The catalog is an authenticated, app-wide endpoint that returns only active
   portrait URLs for published avatars, without profile or ownership metadata.

## Project Structure

### Documentation

```text
specs/016-race-experience/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── math-generation.md
│   └── race-and-championship.md
└── tasks.md

initial_spec/gdd.md
docs/gameplay/
├── feature-math-engine.md
├── spec-math-engine.md
├── feature-race-engine.md
├── spec-race-engine.md
└── spec-game-modes.md
docs/ui/spec-ui-implementation.md
docs/engineering/audio-design.md
```

### Source Code

```text
frontend/src/
├── engine/math/                 # mirrored tier rules and deterministic generator
├── engine/race/                 # round timing and race configuration
├── pages/
│   ├── RaceSetupPage.tsx        # snapshot timing and racer portraits
│   ├── RaceScreenPage.tsx       # timeout submission and avatar track rendering
│   ├── ResultsScreenPage.tsx    # result/championship handoff and retry
│   └── SettingsPage.tsx         # existing timing/audio controls
└── shared/hooks/                # active music-volume synchronization

backend/app/
├── mathematics/                 # equivalent tier operand rules
├── races/                       # answer/result persistence and validation
└── championships/               # championship recording/completion

frontend/src/{engine/math,engine/race,shared/hooks,pages}/*.test.*
backend/tests/{unit,integration}/{mathematics,races,championships}/
```

**Structure Decision**: Extend the existing feature-sliced frontend and backend
domain modules. Keep preferences in browser storage and use existing race,
championship, and mathematics API contracts. No database migration or public
schema shape change is anticipated.

## Implementation Sequence

1. Update the GDD and derived math, race, game-mode, UI, and audio documents with
   the accepted behavior.
2. Change frontend and backend tier 3–5 generation in lockstep; add fixed-seed
   operand-boundary and division-frequency tests.
3. Add the settings control and race-start timing snapshot; handle a single
   timeout through the existing answer flow, including the accessible timer
   display and Training exemption.
4. Reproduce the championship failure through the real result-save sequence,
   fix the failing handoff or state transition, and test retries, standings,
   resume, and final completion.
5. Replace runner dots with avatar portraits/fallbacks, with reduced-motion and
   image-failure coverage.
6. Wire current music playback to saved volume updates; verify music and SFX
   remain independently adjustable and values/defaults are consistent.
7. Run targeted tests, frontend static checks, and the relevant backend test
   suite; run integration coverage when the Docker stack is available.

## Complexity Tracking

No Constitution violations or new architectural components are expected.
