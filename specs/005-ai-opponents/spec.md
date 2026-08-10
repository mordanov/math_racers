# Feature Specification: AI Opponents

**Feature Branch**: `005-ai-opponents`
**Created**: 2026-08-10
**Status**: Draft
**Input**: @docs/gameplay/spec-ai-opponents.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Race Against AI Opponents (Priority: P1)

A player starts a race and competes against one or more AI-controlled opponents. Each opponent moves through the race track based on simulated math performance — answering questions correctly and quickly advances them, while wrong answers leave them stationary. Opponents behave consistently given identical race conditions, enabling fair comparison between runs.

**Why this priority**: Core gameplay value. Without opponents, single-player racing has no competitive element. This story defines the fundamental interactive experience.

**Independent Test**: Start a Quick Race with one opponent. Observe all 8 checkpoints. Confirm the opponent advances or holds position at each checkpoint, and that replaying with the same seed produces identical opponent positions.

**Acceptance Scenarios**:

1. **Given** a race is started with one AI opponent, **When** the player answers a problem correctly with a fast response, **Then** the AI opponent also advances by an amount consistent with its personality and the checkpoint index.
2. **Given** a race is started with one AI opponent, **When** the AI opponent's simulated answer is incorrect, **Then** the opponent does not move (zero distance gained at that checkpoint).
3. **Given** a race with any configuration, **When** the same seed and same opponent personalities are used in two separate runs, **Then** opponent positions at every checkpoint are identical in both runs.
4. **Given** a race is started with zero AI opponents, **When** the race runs through all 8 checkpoints, **Then** no errors occur and the player completes the race normally.

---

### User Story 2 - Distinct Personality Behaviours (Priority: P2)

Players can observe five distinct AI personality types in action during a race. Personalities differ visibly in pacing — some start fast and slow down, others start slow and accelerate, some are erratic, others are steady. This variety makes races feel different and gives players a sense of challenge diversity.

**Why this priority**: Without behavioural variety, all opponents feel identical regardless of their named personality, making the feature hollow. This story is what makes AI opponents interesting and replayable.

**Independent Test**: Run four separate races, each with a single opponent of a different personality (Steady, Speedster, Slow Starter, Unpredictable). Compare checkpoint-by-checkpoint positions to confirm Speedster leads early and slows late, Slow Starter lags early and catches up late, Steady advances uniformly, and Unpredictable varies significantly.

**Acceptance Scenarios**:

1. **Given** a Speedster opponent, **When** observing checkpoints 1–3 vs 7–8, **Then** the Speedster's advancement rate is visibly higher in the first three checkpoints than in the last two.
2. **Given** a Slow Starter opponent, **When** observing checkpoints 1–3 vs 7–8, **Then** the Slow Starter advances more in the later checkpoints than the early ones.
3. **Given** a Steady opponent, **When** observing all 8 checkpoints, **Then** the advancement amounts are roughly uniform with minimal variation.
4. **Given** an Unpredictable opponent across multiple runs with different seeds, **When** comparing checkpoint advancement patterns, **Then** the Unpredictable opponent shows higher variance than any other personality type.
5. **Given** five opponents of the same personality and the same race seed, **When** observing their positions, **Then** each opponent produces a distinct movement sequence (seed-derived per-opponent divergence).

---

### User Story 3 - Personality Configuration Available at Race Setup (Priority: P3)

The game can retrieve the list of available AI opponent personalities from the server at race setup time. This allows the frontend to display personality options with their names and descriptions, and for the backend to serve as the authoritative source for configuration.

**Why this priority**: Enables the frontend to display personality choices dynamically rather than hardcoding them. Lower priority because the personalities themselves are already defined; this story is about exposing them via a standard data endpoint.

**Independent Test**: Call the personalities endpoint. Confirm it returns exactly 5 personality definitions with names and display information.

**Acceptance Scenarios**:

1. **Given** the personalities endpoint is called, **When** the response arrives, **Then** exactly 5 personality definitions are returned with at least a name and a display identifier for each.
2. **Given** the endpoint is called by an unauthenticated client, **When** the response arrives, **Then** the request succeeds (personality list is not private data).

---

### Edge Cases

- What happens when all opponents finish checkpoint 8 at the same accumulated distance? Final positions must be broken deterministically (same seed always produces same result).
- What happens when the difficulty tier adjustment would push an opponent below tier 1 or above the maximum tier? The tier is clamped to the valid range; the opponent still participates.
- What happens when accuracy RNG produces a value outside [0.0, 1.0] due to variability offset? The value is clamped before use; no crash or unexpected result occurs.
- What happens when a race has 5 opponents with identical personalities and the same seed? Each opponent uses an independent RNG sequence so their movements diverge.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST simulate AI opponent movement for each checkpoint (1–8) in a race based on personality parameters, producing a distance value of zero (incorrect) or a positive integer (correct + fast).
- **FR-002**: The system MUST support exactly 5 personality types: Steady, Speedster, Slow Starter, Unpredictable, and Balanced — each with distinct accuracy, pacing, and variability characteristics.
- **FR-003**: The system MUST use a seeded random number generator so that identical inputs (seed, personalities, player tier) always produce identical opponent positions across all checkpoints.
- **FR-004**: The system MUST clamp opponent difficulty tier to a valid range so no opponent ever operates outside the defined tier bounds.
- **FR-005**: The system MUST produce zero movement for a simulated incorrect answer at any checkpoint.
- **FR-006**: A race with zero AI opponents MUST complete without errors.
- **FR-007**: When multiple opponents tie on final accumulated distance, positions MUST be resolved deterministically using a fixed tiebreaker.
- **FR-008**: The system MUST expose an endpoint that returns the 5 personality definitions with their display names.
- **FR-009**: All AI opponent simulation MUST occur on the client (browser), with no backend calls made during an active race.
- **FR-010**: Each opponent in a multi-opponent race MUST receive an independent RNG sequence derived from the shared seed, so opponents of identical personality diverge.

### Key Entities

- **AI Opponent**: A simulated competitor in a race. Has a personality type, an accumulated distance, a current position (checkpoint), and a tier offset applied relative to the player's tier.
- **Personality**: A named configuration defining accuracy probability, speed profile across checkpoints, and a variability range. Five fixed personalities exist; they are not user-created.
- **Race Seed**: A deterministic value provided at race start. Combined with an opponent index to produce per-opponent RNG sequences.
- **Checkpoint Result**: The distance an opponent advances (or does not advance) at a single checkpoint. Zero indicates an incorrect simulated answer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Identical `(seed, personalities, player_tier)` combinations always produce identical opponent positions at every checkpoint across 100% of replays.
- **SC-002**: All 5 personality types produce visually distinct movement patterns observable by comparing checkpoint-by-checkpoint advancement in a single race session.
- **SC-003**: Zero backend network requests are made during an active race simulation (verifiable via browser network inspector).
- **SC-004**: A race with zero AI opponents completes without errors in 100% of attempts.
- **SC-005**: The personalities endpoint returns exactly 5 entries within normal response times during race setup.
- **SC-006**: Tied final positions are resolved to the same ranking on every replay with the same seed (0% non-determinism in tiebreaking).

## Assumptions

- The player's tier is determined before race start and does not change during the race; opponent tier calibration uses a fixed snapshot taken at race start.
- Personalities are a fixed, server-defined set; players cannot create custom personalities in this feature.
- The personalities endpoint is publicly accessible (no authentication required) since personality definitions are non-sensitive game configuration data.
- A race always consists of exactly 8 checkpoints; the simulation loop always runs for exactly 8 steps per opponent.
- The frontend is responsible for consuming opponent simulation results and rendering opponent positions in the race UI; this feature defines the simulation logic and data contract, not the rendering.
- Mobile support and accessibility for the personalities endpoint are handled by the existing platform infrastructure, not this feature.
