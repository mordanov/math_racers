# Research: Mathematics Engine

**Phase**: 0 — Research  
**Branch**: `003-math-engine`  
**Date**: 2026-08-09

---

## Decision 1: Seeded RNG Algorithm

**Decision**: Mulberry32 — a compact, fast, 32-bit seedable PRNG implemented in TypeScript.

**Rationale**: The determinism guarantee requires that identical `(tier, seed, count)` always produces identical output across all browsers and devices, with no reliance on `Math.random()`. Mulberry32 is:
- Fully deterministic from a 32-bit integer seed.
- ~10 lines of pure TypeScript with no dependencies.
- Passes standard PRNG quality tests for games (good distribution, no obvious short cycles at typical seed values).
- Produces float output in [0, 1) directly, matching the pattern `randomInt(rng, min, max) = Math.floor(rng() * (max - min + 1)) + min`.

**Alternatives considered**:
- *xorshift32*: Similar quality, similar size. Mulberry32 has slightly better avalanche on seeds near 0. Either would work; Mulberry32 chosen for marginally better-documented bias properties.
- *seedrandom (npm)*: Larger, adds a dependency, unnecessary for a 32-bit seed space. Violates Constitution §XIX (no unnecessary dependencies).
- *LCG (linear congruential)*: Simplest, but known spectral lattice structure means consecutive values are correlated in low-dimensional projections — acceptable for this use case but Mulberry32 is the same size and strictly better.

---

## Decision 2: Module Location (Frontend)

**Decision**: `frontend/src/engine/math/` — a pure TypeScript module with no React dependency.

**Rationale**: ADR-004 mandates that mathematical challenges are a frontend concern. The engine has no UI, no state management, no side-effects — it is a pure computation. Placing it in `engine/math/` (separate from `components/` and `hooks/`) makes the boundary explicit and keeps it independently testable with Vitest without mounting React components.

**Alternatives considered**:
- `frontend/src/services/math/`: "Services" in this project typically implies I/O or network calls. Pure computation is not a service.
- Shared package: No monorepo setup exists; the backend reference generator is Python, so sharing code would add complexity. Constitution §VI (simplicity) rules this out.

---

## Decision 3: Backend Reference Generator Language

**Decision**: Python — plain functions in `backend/app/mathematics/` domain module, mirroring the frontend algorithm exactly.

**Rationale**: The backend reference endpoint (`GET /api/v1/problems`) must produce identical output to the frontend for the same seed. Python's integer arithmetic is deterministic across platforms. The Mulberry32 algorithm translates directly to Python with identical integer semantics using a 32-bit mask (`& 0xFFFFFFFF`). No separate library needed.

**Alternatives considered**:
- Sharing a Wasm module: Over-engineered for a reference endpoint that is never in the gameplay critical path (Constitution §VI).
- Storing pre-generated sets: Defeats the purpose of seed-based generation and wastes storage.

---

## Decision 4: Operation Picker Distribution

**Decision**: Uniform random pick from the allowed operations list for the given tier, using the seeded RNG.

**Rationale**: The spec does not prescribe a weighted distribution. Uniform distribution is the simplest correct solution (Constitution §VI) and keeps problem sets varied. If future GDD updates require weighted distributions (e.g., more addition at lower tiers), the `pickOperation` function is the single change point.

**Alternatives considered**:
- Weighted distribution: No evidence in GDD or spec that non-uniform weighting is required. Deferred unless documented.
- Round-robin cycling: Would reduce perceived randomness and break the determinism guarantee if cycle state were not part of the seed.

---

## Decision 5: Duplicate Detection Scope

**Decision**: Compare the immediately preceding problem only (`lastProblem`), matching `(operation, operand_a, operand_b)`. Retry up to 10 times; accept duplicate on retry exhaustion.

**Rationale**: Spec §Duplicate prevention explicitly defines this scope and the 10-retry cap. No interpretation needed. The operand space is always larger than 1 for all tiers, so exhaustion is pathological (only possible if `count` greatly exceeds the problem space, which is not a supported use case).

---

## Decision 6: Frontend Testing Framework

**Decision**: Vitest with no DOM — pure unit tests for all engine functions.

**Rationale**: The math engine has no UI surface. Vitest is already the project's test runner (devDependency in `package.json`). Tests cover: determinism (same seed → same output), tier constraints (operation types, operand ranges), division safety, duplicate prevention, answer validation, and tier selection logic.

---

## Decision 7: Backend API — Problem Endpoint Input Validation

**Decision**: Pydantic query-parameter model; `tier` validated to `[1, 6]` (raises HTTP 422 on violation); `count` validated to `[0, 100]` (prevents abuse); `seed` accepted as any 32-bit unsigned integer.

**Rationale**: Spec §Edge Case 6 and §API Endpoint both specify HTTP 422 for out-of-range tier. Capping `count` at 100 prevents trivial DoS via large problem-set requests without any documented gameplay need for sets larger than 100. Constitution §XV (security, input validation at every API boundary).

**Alternatives considered**:
- Unlimited `count`: No gameplay requirement exists for sets > 8–50 problems. Unbounded is a security risk.
