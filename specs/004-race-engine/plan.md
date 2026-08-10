# Implementation Plan: Race Engine

**Branch**: `004-race-engine` | **Date**: 2026-08-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/004-race-engine/spec.md`

---

## Summary

Implement the client-side Race Engine that enforces a 6-state race state machine, drives a monotonic `requestAnimationFrame` game clock, calculates per-obstacle movement from response time and correctness, simulates deterministic AI runners using a seeded Gaussian noise model, and persists a race summary to the backend after each completed race. The engine lives entirely in `frontend/src/engine/race/`; the backend receives only the summary POST at race completion.

---

## Technical Context

**Language/Version**: TypeScript 5.x (frontend); Python 3.12 (backend)  
**Primary Dependencies**: React 18, Vite, Vitest (frontend); FastAPI, SQLAlchemy 2, Pydantic 2, asyncpg (backend)  
**Storage**: PostgreSQL — new `races` + `race_participants` tables  
**Testing**: Vitest (frontend unit tests); pytest + pytest-asyncio (backend)  
**Target Platform**: Browser (Chrome, Edge, Firefox, Safari — current stable)  
**Project Type**: Web application (React SPA + FastAPI REST API)  
**Performance Goals**: 60 FPS target; 30 FPS minimum; problem generation < 1 ms; audio feedback latency < 50 ms  
**Constraints**: No API calls during active race (RACING state); race simulation fully client-side; clock must be tab-pause-aware  
**Scale/Scope**: 1–5 participants per race; 8 obstacles per race; 6 difficulty tiers

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| § IV Architecture — modular monolith, no circular deps | ✅ PASS | New `engine/race/` module mirrors existing `engine/math/` structure |
| § VI Simplicity — no unnecessary abstractions | ✅ PASS | Plain TS discriminated union for states; no external state machine library |
| § IX Backend principles — no gameplay logic in backend | ✅ PASS | Backend receives only the summary record; all simulation is frontend-only |
| § X Frontend principles — rendering/logic separated | ✅ PASS | Engine is pure TS; `useRaceEngine` hook bridges to React |
| § XI Gameplay — must follow GDD | ✅ PASS | Movement tiers, state machine, 8 obstacles all match spec-race-engine.md |
| § XIV Data ownership — backend is source of truth | ✅ PASS | Race summary POST-ed to backend once; no client-side authoritative store |
| § XVIII Testing — automated tests required | ✅ PASS | Unit tests for state machine, movement calc, clock, AI sim; API integration test |
| § XIX Dependencies — no unnecessary libs | ✅ PASS | Box-Muller uses existing seeded RNG; no new runtime dependencies |
| § XXII Versioning — API versioned | ✅ PASS | Endpoint at `/api/v1/races/` |

**No violations. Gates clear.**

---

## Project Structure

### Documentation (this feature)

```text
specs/004-race-engine/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── race-summary-api.md  ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code

```text
frontend/
├── src/
│   └── engine/
│       ├── math/              ← existing (003-math-engine)
│       └── race/              ← NEW
│           ├── index.ts       ← public API exports
│           ├── types.ts       ← RaceState, RunnerState, RaceConfig, RaceSummary, …
│           ├── constants.ts   ← OBSTACLE_COUNT, MAX_TRACK_DISTANCE, tier thresholds
│           ├── stateMachine.ts ← transition table + transition()
│           ├── movement.ts    ← calculateMovement() pure function
│           ├── clock.ts       ← GameClock class (tick, pause, resume)
│           ├── aiRunner.ts    ← simulateAiObstacle() using seeded Gaussian
│           ├── raceEngine.ts  ← createRaceEngine() — assembles all sub-modules
│           └── hooks/
│               └── useRaceEngine.ts  ← React hook (tick via rAF, exposes API)
└── tests/
    └── engine/
        └── race/
            ├── stateMachine.test.ts
            ├── movement.test.ts
            ├── clock.test.ts
            ├── aiRunner.test.ts
            └── raceEngine.integration.test.ts

backend/
└── app/
    └── races/               ← NEW bounded context (mirrors app/mathematics/)
        ├── __init__.py
        ├── models.py        ← SQLAlchemy Race + RaceParticipant models
        ├── schemas.py       ← Pydantic request/response schemas
        ├── repository.py    ← RaceRepository (async, SQLAlchemy)
        ├── domain_service.py ← RaceDomainService (validation, persistence logic)
        └── presentation/
            └── api/v1/
                └── races.py ← POST /api/v1/races/ endpoint

backend/alembic/versions/
└── <timestamp>_add_races_tables.py  ← new migration

backend/tests/
└── races/
    ├── test_domain_service.py
    ├── test_repository.py
    └── test_api_races.py
```

**Structure Decision**: Option 2 (web application) — existing backend/frontend split. New code mirrors established conventions: a `races/` bounded context on the backend, an `engine/race/` module on the frontend.

---

## Complexity Tracking

> No constitution violations. This section is empty.

---

## Phase 0: Research — Complete

See [research.md](research.md).

All technical unknowns resolved:

| Unknown | Decision |
|---------|---------|
| State machine approach | Plain TS transition table — no external library |
| Game clock implementation | `requestAnimationFrame` accumulator; delta clamped to 100 ms |
| AI Gaussian noise | Box-Muller transform over existing `createRng` PRNG |
| Race summary persistence | Frontend assembles; single POST after RESULTS transition |
| Seeded RNG split | Two independent RNG instances from same seed (`seed` for problems, `seed + 1` for AI) |
| Module location | `frontend/src/engine/race/` |
| React integration | `useRaceEngine` hook |

---

## Phase 1: Design — Complete

### Sub-modules

**`stateMachine.ts`**
- `LEGAL_TRANSITIONS`: `Record<RaceState, Set<RaceState>>`
- `transition(from, to)`: throws `RaceStateError` on illegal transition

**`movement.ts`**
- `calculateMovement(isCorrect, responseTimeMs)`: returns `{ tier, distanceMetres }`
- Pure function — no side effects, no external state

**`clock.ts`**
- `GameClock` class: `tick(timestamp)`, `pause()`, `resume()`, `reset()`, `getMs()`
- Accumulates delta per frame; clamps delta to `FRAME_DELTA_CAP_MS`
- `pause()`/`resume()` driven by `visibilitychange` event

**`aiRunner.ts`**
- `simulateAiObstacle(personality, tier, rng)`: returns `{ isCorrect, responseTimeMs }`
- Gaussian sample via Box-Muller; clipped to `[0, ∞)`
- `isCorrect` drawn from `Math.random()` seeded via RNG (Bernoulli with `accuracyRate`)

**`raceEngine.ts`**
- `createRaceEngine(config)` factory — returns engine instance with:
  - `transition(toState)` — delegates to stateMachine
  - `tick(timestamp)` — advances clock; AI runner updates post-player-submit
  - `submitAnswer({ isCorrect })` — records obstacle result, advances obstacle index
  - `getState()` — returns current `RaceEngineState` snapshot
  - `getSummary()` — returns `RaceSummary` (only valid in RESULTS state)

**`useRaceEngine.ts`**
- Wraps `createRaceEngine` in a `useRef`; calls `engine.tick()` via `useAnimationFrame`
- Exposes derived state as React state (updated each frame)
- Registers/deregisters `visibilitychange` listener for clock pause/resume

### Backend

**`models.py`** — `Race` + `RaceParticipant` SQLAlchemy models (see data-model.md)

**`schemas.py`** — `RaceSummaryRequest` (Pydantic, matches contract), `RaceSummaryResponse`

**`repository.py`** — `RaceRepository.create(summary)` — upsert-safe (checks for existing `race_id`, raises `RaceAlreadyExistsError` on duplicate)

**`domain_service.py`** — `RaceDomainService.persist_race(summary)` — validates positions are unique, delegates to repository

**`races.py`** (endpoint) — POST `/api/v1/races/`; calls domain service; returns 201 or 4xx per contract

**Migration** — adds `races` and `race_participants` tables

---

## Post-Design Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| § IV Architecture | ✅ PASS | `engine/race/` modules are self-contained; no circular imports |
| § VI Simplicity | ✅ PASS | Each sub-module is < 80 lines; no speculative features |
| § IX Backend | ✅ PASS | `races.py` endpoint delegates to domain service; no logic in controller |
| § X Frontend | ✅ PASS | `raceEngine.ts` is pure TS; hook and components are separate layers |
| § XI Gameplay | ✅ PASS | All tiers, distances, and edge cases match spec |
| § XVIII Testing | ✅ PASS | Unit tests per sub-module; integration test for full race loop; API test for endpoint |

**All gates clear post-design.**
