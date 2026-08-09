# Feature Specification: Mathematics Engine

**Feature Branch**: `003-math-engine`  
**Created**: 2026-08-09  
**Status**: Draft  
**Input**: docs/gameplay/spec-math-engine.md

## Clarifications

### Session 2026-08-09

- Q: Should the math engine record elapsed response time, classify it into timing categories, or leave timing entirely to the race engine? → A: Math engine records elapsed time only; race engine interprets it into movement tiers.
- Q: What observability is required from the math engine? → A: Minimal structured logging of errors only (generation failures, unexpected non-numeric input); no metrics in scope.
- Q: What concurrent-session target applies to the math engine? → A: Not applicable — browser runtime isolation guarantees per-tab independence; no concurrency target needed for this engine.
- Q: Should the "no negative subtraction results" constraint be an explicit functional requirement or remain an assumption? → A: Explicit FR — subtraction operands must be ordered so the result is always ≥ 0.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Problem Generation (Priority: P1)

A player (or the game system) requests a set of maths problems for a race session. Given a tier level and a seed value, the engine always produces the exact same sequence of problems — so two players with the same seed get identical challenges, and replaying a session reproduces the same questions.

**Why this priority**: Deterministic generation is the foundation of fair multiplayer racing and reproducible training sessions. Nothing else works correctly without it.

**Independent Test**: Can be tested by generating a problem set twice with the same (tier, seed, count) and asserting byte-for-byte identical output, plus once with a different seed and asserting the output differs.

**Acceptance Scenarios**:

1. **Given** a tier and seed, **When** a problem set is generated twice, **Then** both sets are identical in operation, operands, and answers.
2. **Given** a tier and a different seed, **When** a problem set is generated, **Then** the output differs from the previous seed's output.
3. **Given** `count = 0`, **When** a problem set is generated, **Then** an empty set is returned without error.

---

### User Story 2 - Tier-Appropriate Problem Content (Priority: P1)

A player at a given skill tier receives problems suited to that level: Tier 1 gets addition-only with small numbers, higher tiers progressively unlock subtraction, multiplication, and division with larger operands. Division problems always have whole-number answers.

**Why this priority**: Incorrect tier content breaks the educational contract and the adaptive difficulty system. This is a correctness invariant, not an enhancement.

**Independent Test**: Can be tested by generating 100+ problems per tier and asserting operation types, operand ranges, and answer integrity for each tier independently.

**Acceptance Scenarios**:

1. **Given** Tier 1, **When** problems are generated, **Then** all operations are addition and all operands are in [1, 10].
2. **Given** Tier 4+, **When** problems are generated, **Then** all four operations appear across a large enough set, and every division answer is a whole number.
3. **Given** any tier with division, **When** a division problem is generated, **Then** the divisor is never zero and the answer is always an integer.
4. **Given** Tier 6 with no parent configuration, **When** problems are generated, **Then** Tier 5 behaviour is used without error.
5. **Given** any tier that includes subtraction, **When** a subtraction problem is generated, **Then** operand_a ≥ operand_b and the answer is always ≥ 0.

---

### User Story 3 - No Consecutive Duplicate Problems (Priority: P2)

Within a single problem set, no two consecutive problems are identical (same operation and same operands). This keeps sessions varied and prevents trivial repetition.

**Why this priority**: Consecutive duplicates degrade the learning experience but do not break core functionality; hence P2.

**Independent Test**: Can be tested by generating problem sets of 50+ problems and scanning for any pair of consecutive identical (operation, operand_a, operand_b) tuples.

**Acceptance Scenarios**:

1. **Given** any tier and seed, **When** a problem set is generated, **Then** no two consecutive problems share the same operation and operands.
2. **Given** a highly constrained tier (e.g., Tier 1, count = 20), **When** the retry limit is reached, **Then** a duplicate is accepted rather than looping infinitely.

---

### User Story 4 - Immediate Answer Validation (Priority: P1)

A player types an answer and the game responds instantly — correct or incorrect — with no perceptible delay. Validation happens entirely client-side without a network round-trip.

**Why this priority**: Perceived responsiveness is critical to the racing game experience; any delay feels broken.

**Independent Test**: Can be tested by submitting correct and incorrect answers (including non-numeric input) and asserting the validation result and its correctness flag.

**Acceptance Scenarios**:

1. **Given** a problem and the correct integer answer, **When** the player submits it, **Then** validation returns `correct: true` within 1 ms.
2. **Given** a problem and an incorrect integer, **When** the player submits it, **Then** validation returns `correct: false` and the player does not advance.
3. **Given** non-numeric input (e.g., letters, empty string), **When** the player submits it, **Then** validation returns `correct: false` with reason `not_a_number` and never throws.

---

### User Story 5 - Adaptive Tier Selection (Priority: P2)

Before a race, the system selects an appropriate difficulty tier based on the player's recent skill score, or uses a parent/teacher override if one is set. The tier does not change during an active race.

**Why this priority**: Adaptive difficulty is a key engagement feature, but it operates at session setup time, not during gameplay, making it lower risk.

**Independent Test**: Can be tested by calling tier selection with various skill scores and override values and asserting the returned tier against expected rules.

**Acceptance Scenarios**:

1. **Given** a skill score ≥ 0.90 and current tier < 6, **When** tier is selected, **Then** tier advances by 1.
2. **Given** a skill score < 0.60 and current tier > 1, **When** tier is selected, **Then** tier decreases by 1.
3. **Given** a parent override of 3, **When** tier is selected, **Then** tier is 3 regardless of skill score.
4. **Given** a parent override outside [1, 6], **When** tier is selected, **Then** it is clamped silently to [1, 6].
5. **Given** an active race in progress, **When** any event occurs, **Then** the tier does not change.

---

### Edge Cases

- What happens when the seed produces the same problem twice in a row? → Retry loop regenerates; after 10 retries, the duplicate is accepted to prevent infinite loops.
- How does the system handle `count = 0`? → Returns an empty ProblemSet; valid for training-mode preview.
- What happens if operands would overflow the tier's documented range? → Operands are clamped to the tier maximum.
- How does Tier 6 behave without a parent configuration? → Falls back to Tier 5 behaviour silently.
- What if a parent override value is outside [1, 6]? → Clamped silently client-side; rejected with HTTP 422 via the backend API.
- What happens with concurrent races sharing the same seed? → Each race holds its own independent ProblemSet; no shared mutable state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST generate a problem set entirely client-side with no network call during active gameplay.
- **FR-002**: Given identical `(tier, seed, count)` inputs, the engine MUST always produce an identical problem sequence (determinism guarantee).
- **FR-003**: The engine MUST produce only operation types permitted for the given tier (see Difficulty Tiers).
- **FR-004**: The engine MUST keep all operands within the documented range for the given tier.
- **FR-005**: Division problems MUST always have integer answers; division by zero MUST never occur.
- **FR-006**: The engine MUST prevent two consecutive problems from having the same operation and operands; after 10 retries per slot the duplicate is accepted.
- **FR-007**: Answer validation MUST parse player input as an integer, return `correct: false` on non-numeric input, and complete within 1 ms. The engine MUST also record the elapsed time from problem render to validation call; timing interpretation into movement categories is the responsibility of the race engine.
- **FR-008**: Tier selection MUST apply the parent/teacher override first; if not set, MUST use the skill-score thresholds (≥ 0.90 → +1, < 0.60 → −1, else unchanged).
- **FR-009**: Tier values MUST be clamped to [1, 6]; override values outside this range MUST be rejected with HTTP 422 via the API.
- **FR-010**: Tier MUST NOT change during an active race session.
- **FR-011**: `count = 0` MUST return a valid empty ProblemSet without error.
- **FR-012**: Tier 6 without parent configuration MUST fall back to Tier 5 behaviour.
- **FR-013**: Each race session MUST hold its own independent ProblemSet instance with no shared mutable state.
- **FR-014**: The engine MUST emit structured error logs for generation failures and unexpected non-numeric validation inputs; no other metrics or tracing are in scope.
- **FR-015**: For subtraction problems, operands MUST be ordered so that the result is always ≥ 0 (operand_a ≥ operand_b at generation time).

### Key Entities

- **Problem**: A single maths challenge with operation, two operands, an integer answer, a tier, and a seed. Identity is defined by `(operation, operand_a, operand_b)` for duplicate-detection purposes.
- **ProblemSet**: An ordered collection of Problems sharing a common seed, tier, and count. Immutable once generated.
- **Tier**: An integer in [1, 6] representing difficulty; determines allowed operations and operand ranges.
- **Skill Score**: A floating-point value in [0, 1] representing a player's recent performance, used to drive adaptive tier adjustment.
- **Parent Override**: An optional integer in [1, 6] set by a parent or teacher to pin or cap difficulty.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Generating the same (tier, seed, count) twice always yields identical problem sets — verified by automated regression tests with 100% pass rate.
- **SC-002**: Answer validation completes in under 1 ms on the reference test device (measured from input submission to result availability).
- **SC-003**: No division problem in any generated set has a non-integer answer or a zero divisor — verified across 10,000 generated problems per tier.
- **SC-004**: No two consecutive problems in any generated set share identical operation and operands — verified across 10,000 generated problem sets.
- **SC-005**: Tier selection correctly applies skill-score thresholds and parent overrides in 100% of unit test cases covering all boundary conditions.
- **SC-006**: The reference backend endpoint returns a valid ProblemSet for valid inputs and HTTP 422 for out-of-range tier overrides — verified by API integration tests.

## Assumptions

- Problem generation runs entirely in the browser; the backend endpoint is a reference tool only and is not in the critical path for gameplay.
- The seeded random number generator (RNG) is a deterministic algorithm agreed upon before implementation (e.g., a seedable LCG or Xorshift); the specific algorithm choice is a planning-phase decision.
- Tier 6 custom operand ranges are stored and served by the backend; the client fetches them before race setup, not during.
- Skill score computation is handled by a separate system (adaptive difficulty engine); this feature only consumes the score.
- The player is always a single human user per race session; no AI or bot opponents are in scope for this engine.
- Concurrent-session isolation is guaranteed by the browser runtime (one engine instance per tab); no explicit concurrency target is required for the math engine itself.
- Negative results in subtraction (Tier 2+) are structurally prevented by operand ordering (operand_a ≥ operand_b); this is now captured as FR-015.
