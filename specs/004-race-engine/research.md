# Research — Race Engine

**Branch**: `004-race-engine` | **Date**: 2026-08-10

---

## 1. State Machine Implementation

**Decision**: Plain TypeScript discriminated union + transition table (no external library).

**Rationale**: The state machine has exactly 6 states and a fixed, small transition table. A record keyed by `[from][to]` is sufficient. Using a library (XState, Robot) would introduce a dependency for a problem that can be solved with ~30 lines.

**Alternatives considered**:
- XState — powerful but heavyweight; adds 30 kB+ and a learning curve for a fixed state graph.
- Class-based inheritance — more lines for no benefit; harder to tree-shake.

---

## 2. Game Clock

**Decision**: Accumulator pattern using `requestAnimationFrame`. Each frame delta is clamped to 100 ms to prevent large jumps after tab-switch or browser throttling.

**Rationale**: `performance.now()` is used per-frame for the delta, but the clock is an accumulated counter stored in React state. This keeps the clock monotonically increasing and immune to system-clock adjustments. The spec explicitly says `requestAnimationFrame` drives the clock.

**Alternatives considered**:
- `Date.now()` — affected by system clock changes; not monotonic.
- `setInterval` — not frame-aligned; timer fires can be batched by the browser.

**Tab-focus integration**: `document.addEventListener('visibilitychange')` pauses accumulation when `document.hidden === true`; resumes on focus. No delta is added during the hidden window.

---

## 3. AI Runner Simulation

**Decision**: Gaussian noise via Box-Muller transform using the seeded RNG (`createRng`) already implemented in `frontend/src/engine/math/rng.ts`.

**Rationale**: The existing `createRng` is a deterministic Mulberry32 PRNG. Wrapping it in Box-Muller gives Gaussian noise without adding a dependency. This satisfies the determinism requirement (same seed → same noise sequence).

**Alternatives considered**:
- Lookup table for variance — deterministic but less natural-looking distribution.
- Math.random() — non-deterministic; violates the spec's determinism requirement.

**Update order**: AI runners are processed sequentially (index order) per obstacle after the player submits, one per animation tick, to avoid simultaneous visual updates.

---

## 4. Race Summary Persistence

**Decision**: Race summary is assembled in the frontend engine, then POST-ed to the backend `/api/v1/races/` endpoint after the FINISHING → RESULTS transition.

**Rationale**: The spec states "no API calls during active race." The summary is built entirely in memory during the race and flushed once all runners finish. The backend endpoint validates the payload and persists it.

**Alternatives considered**:
- Persist locally then sync — adds complexity; backend is the source of truth (Constitution § XIV).
- Fire-and-forget without validation — acceptable for the race summary use case since the player is already on the Results screen; a retry on failure suffices.

---

## 5. Seeded RNG Strategy (Race vs Problem)

**Decision**: Use two independent RNG instances derived from the race seed: one for problem generation (already done via `generateProblemSet`), one for AI variance. Both are initialised from the same seed with a deterministic offset (`seed + 1` for AI RNG).

**Rationale**: Separating concerns avoids state contamination between problem generation and AI variance draws. Using `seed + 1` is simple and reproducible.

**Alternatives considered**:
- Single shared RNG — problem generation and AI variance draws would interfere if count or order changes.
- Hash-derived sub-seeds — cleaner cryptographically but overkill for a game.

---

## 6. Module Location

**Decision**: Race engine lives under `frontend/src/engine/race/`.

**Rationale**: `frontend/src/engine/math/` already exists. Sibling directory `race/` keeps domain concerns parallel and consistent with the existing convention. The backend receives only the summary record; all live simulation logic stays in the frontend.

**Alternatives considered**:
- `frontend/src/game/` — too generic; conflicts with future game-mode modules.
- `frontend/src/race/` — puts business logic at the top-level `src/` rather than inside `engine/`.

---

## 7. React Integration Pattern

**Decision**: Encapsulate race state in a single `useRaceEngine` hook. Components read derived state; they do not write to the engine directly. All transitions go through the hook's public API.

**Rationale**: Consistent with the existing frontend pattern (see `frontend/src/engine/math/` — pure functions consumed by hooks). Keeps the engine testable without React (plain TypeScript unit tests) while still being usable from components.

**Alternatives considered**:
- Zustand/Redux store — adds a dependency; hook is sufficient for a single-race lifecycle.
- Component state — logic leaks into JSX; impossible to unit-test without a renderer.

---

## NEEDS CLARIFICATION — All Resolved

All technical unknowns resolved above. No open items.
