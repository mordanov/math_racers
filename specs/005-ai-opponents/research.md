# Research: AI Opponents

**Branch**: `005-ai-opponents` | **Date**: 2026-08-10
**Status**: Complete — no NEEDS CLARIFICATION items in spec

---

## Decision 1: AiPersonality type extension strategy

**Decision**: Extend the existing `AiPersonality` interface in `frontend/src/engine/race/types.ts` with two new fields: `speedProfile` (union literal) and `tierOffset` (number). Do not create a separate mapping type.

**Rationale**: The existing type already carries `accuracyRate`, `baseResponseTimeMs`, and `responseTimeVarianceMs`. The spec adds two orthogonal dimensions (`speedProfile` for checkpoint-index-aware response time sampling, `tierOffset` for difficulty calibration). Extending in-place keeps the simulation call-site unchanged for callers that already construct `AiPersonality` objects.

**Alternatives considered**:
- Separate `PersonalityDefinition → AiPersonality` mapping: adds indirection with no benefit for this codebase scale.
- Replacing `AiPersonality` entirely: breaks the existing `simulateAiObstacle` call-site in `raceEngine.ts` unnecessarily.

---

## Decision 2: simulateAiObstacle signature — add checkpointIndex

**Decision**: Update `simulateAiObstacle(personality, rng)` to `simulateAiObstacle(personality, checkpointIndex, rng)`. The function gains checkpoint-aware response time sampling via `sampleResponseTime` logic matching the spec algorithm.

**Rationale**: Speed profiles (front_loaded, back_loaded, uniform, random) require the checkpoint index to compute the base response time via lerp or uniform sample. The existing Gaussian noise approach (`baseResponseTimeMs + gaussianNoise * responseTimeVarianceMs`) is replaced by the spec's `sampleResponseTime` + speed multiplier logic, which already matches the `calculateMovement` distance thresholds (2s/4s/6s).

**Alternatives considered**:
- Keep Gaussian noise, model personalities purely by `baseResponseTimeMs` values: loses front_loaded/back_loaded arc behaviour that makes personalities visibly distinct.
- Pass checkpoint index via a closure: unnecessarily complex.

---

## Decision 3: Per-opponent RNG — one RNG per AI runner

**Decision**: Replace the single shared `aiRng = createRng(config.seed + 1)` in `raceEngine.ts` with per-opponent RNGs: `createRng(config.seed + participantIndex + 1)` (offset by participant array index, starting from 1 to avoid collision with the problem set RNG at `config.seed`).

**Rationale**: The spec explicitly requires that "each opponent in a multi-opponent race MUST receive an independent RNG sequence derived from the shared seed". With a single shared RNG the second AI opponent's results depend on how many calls the first opponent made — so identical personalities diverge only accidentally. Per-opponent RNGs guarantee deterministic, independent sequences.

**Alternatives considered**:
- Per-obstacle per-opponent RNG re-seeded from `seed + opponentIndex * 100 + obstacleIndex`: over-engineered; the stateful RNG already gives independence per obstacle when one RNG per opponent is used.
- Splitting the seed with a hash: unnecessary complexity; index offset suffices.

---

## Decision 4: Tiebreaking — runnerId lexicographic comparison

**Decision**: Update `getSummary()` in `raceEngine.ts` tiebreaker from array insertion order to lexicographic comparison of `runnerId` strings.

**Rationale**: The spec requires deterministic tiebreaking that does not depend on array insertion order (which can vary). `runnerId` is a stable string that callers control; lexicographic sort is deterministic across replays.

**Alternatives considered**:
- Timestamp-based tiebreaker: non-deterministic.
- Keep array insertion order: passes for a fixed set of participants but the spec says to use `id`, and the existing pattern is not documented as intentional.

---

## Decision 5: Backend personalities endpoint — static data, no DB

**Decision**: `GET /api/v1/opponents/personalities` returns a hardcoded list of 5 personality definitions from a module-level constant. No database table, no repository. The endpoint is unauthenticated (personality definitions are non-sensitive game config).

**Rationale**: Personality parameters are fixed game constants defined in the spec. They do not vary per user, per tier, or over time. Introducing a DB table would add schema migration and repository overhead for data that will only change when the spec changes (which requires a code deploy anyway).

**Alternatives considered**:
- DB-backed personalities with admin CRUD: over-engineered for fixed game config; contradicts Simplicity principle.
- Personalities embedded in frontend only (no endpoint): violates the spec's FR-008 and the Constitution's principle against duplicating business logic — the backend is authoritative.

---

## Decision 6: Backend module placement — app/opponents/

**Decision**: New backend module at `backend/app/opponents/` with `schemas.py` and `presentation/api/v1/opponents.py`. Router registered in `main.py`.

**Rationale**: Matches the existing module pattern (`app/mathematics/`, `app/races/`, `app/accounts/`). Keeps domain code separate from presentation. The `opponents` subdomain owns personality definitions.

**Alternatives considered**:
- Adding to `app/races/`: opponents are a distinct subdomain from race persistence; co-locating would couple unrelated concerns.
- Single-file in `app/presentation/api/v1/opponents.py`: violates the project pattern of keeping schemas in domain modules.

---

## Decision 7: Frontend personalities.ts — static constants, fetched at race setup

**Decision**: `frontend/src/engine/race/personalities.ts` exports the 5 named personality objects as TypeScript constants (for offline/dev use and for typing), plus a `fetchPersonalities()` function that calls `GET /api/v1/opponents/personalities` and returns the server's authoritative list.

**Rationale**: Having static constants locally allows tests to run without a backend. Having `fetchPersonalities()` honours the spec requirement that the backend is the authoritative source for race setup. At race start, the frontend fetches from the server; the local constants are the fallback and the test fixture.

**Alternatives considered**:
- No local constants, always fetch: tests require a running backend.
- No fetch, only local constants: violates FR-008 and the backend-as-authoritative-source principle.
