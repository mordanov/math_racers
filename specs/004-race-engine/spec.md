# Feature Specification: Race Engine

**Feature Branch**: `004-race-engine`  
**Created**: 2026-08-10  
**Status**: Draft  
**Input**: User description: "@docs/gameplay/spec-race-engine.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Complete a Quick Race (Priority: P1)

A player selects Quick Race mode, progresses through exactly 8 obstacle problems, and reaches the Results screen. At each obstacle the player submits an answer; their runner moves forward by an amount that reflects both correctness and response speed. At the end, all participant positions and distances are summarised on the Results screen.

**Why this priority**: This is the core game loop. Every other mode and feature depends on a working end-to-end race; it is the minimum viable product.

**Independent Test**: Can be fully tested by starting a Quick Race, answering all 8 questions, and confirming the Results screen shows correct positions and distances for both the player and AI runners.

**Acceptance Scenarios**:

1. **Given** the application is in IDLE state, **When** the player selects Quick Race, **Then** the game transitions through LOBBY → COUNTDOWN → RACING in order.
2. **Given** the player is in RACING state, **When** they answer a problem correctly in under 2 seconds, **Then** their runner advances exactly 18 m (Perfect tier).
3. **Given** the player is in RACING state, **When** they answer a problem correctly in 2–4 s, **Then** their runner advances 15 m (Excellent tier).
4. **Given** the player is in RACING state, **When** they answer a problem correctly in 4–6 s, **Then** their runner advances 12 m (Good tier).
5. **Given** the player is in RACING state, **When** they answer a problem correctly in over 6 s, **Then** their runner advances 9 m (Slow correct tier).
6. **Given** the player is in RACING state, **When** they answer a problem incorrectly, **Then** their runner does not move (0 m) and their distance never decreases.
7. **Given** the first runner completes obstacle 8, **When** the remaining runners finish obstacle 8, **Then** the game transitions to RESULTS and shows final positions.

---

### User Story 2 — Race Against AI Runners (Priority: P2)

A player races against AI opponents whose behaviour is driven by a seeded algorithm. AI runners respond to problems with simulated accuracy and response times derived from the difficulty tier and a personality variance. The AI updates are staggered to prevent visual stacking.

**Why this priority**: AI opponents are essential for meaningful competition in all solo modes; without them the race is a solo time trial with no positional context.

**Independent Test**: Can be tested by running a Quick Race, observing that AI runners move at each obstacle, and confirming that running the same seed in Training mode twice produces identical AI results.

**Acceptance Scenarios**:

1. **Given** a race is in RACING state, **When** each obstacle resolves, **Then** each AI runner's movement is calculated from their simulated accuracy and response time using the same movement tiers as the player.
2. **Given** the same race seed and difficulty tier, **When** the race is replayed in Training mode, **Then** AI runners produce the exact same distances and positions each time.
3. **Given** multiple AI runners finish an obstacle simultaneously, **When** their on-screen positions are updated, **Then** they are updated sequentially (not simultaneously) to avoid visual stacking.

---

### User Story 3 — Race State Machine Enforcement (Priority: P2)

The race engine enforces a strict state machine. Only legal transitions are permitted; any attempt to jump to a state out of sequence is rejected.

**Why this priority**: State integrity prevents exploits (e.g., skipping the countdown) and ensures data consistency across all race modes.

**Independent Test**: Can be tested in isolation by attempting to trigger illegal transitions (e.g., IDLE → RACING, RESULTS → RACING) and confirming they are rejected with no state change.

**Acceptance Scenarios**:

1. **Given** the engine is in IDLE state, **When** an attempt is made to skip directly to RACING, **Then** the transition is rejected and IDLE state is preserved.
2. **Given** the engine is in COUNTDOWN state, **When** an attempt is made to return to IDLE, **Then** the transition is rejected.
3. **Given** the engine is in RESULTS state, **When** an attempt is made to jump directly to RACING, **Then** the transition is rejected; the player must return to LOBBY first.
4. **Given** the engine is in any state, **When** a valid next-state transition is requested, **Then** the transition succeeds and the new state is active.

---

### User Story 4 — Game Clock Accuracy (Priority: P3)

The race uses a monotonic game clock that starts when "GO!" appears. Per-obstacle timing starts when the problem card becomes visible and stops when the player submits. The clock is not disrupted by tab visibility changes; those are handled by a separate pause mechanism.

**Why this priority**: Accurate timing is required for correct movement tier assignment. It is testable independently of the full race loop.

**Independent Test**: Can be tested by recording the time between problem visibility and player submission and confirming the correct movement tier is applied.

**Acceptance Scenarios**:

1. **Given** the countdown reaches zero, **When** "GO!" is displayed, **Then** the game clock starts.
2. **Given** a problem card becomes visible, **When** the player submits an answer, **Then** the elapsed time for that obstacle is used to determine the movement tier.
3. **Given** the browser tab loses focus during a race, **When** the tab regains focus, **Then** the per-obstacle clock resumes from where it paused (not from zero and not including the unfocused duration).

---

### User Story 5 — Race Summary Persisted (Priority: P3)

After every race, a summary record is saved. It captures the seed, difficulty tier, mode, timestamps, and per-participant outcomes (position, correctness, average response time, total distance, XP earned).

**Why this priority**: The summary is the foundation for progress tracking, leaderboards, and analytics; it is independent of the live race loop.

**Independent Test**: Can be tested by completing a race and confirming the persisted record matches the observed in-race values for all participants.

**Acceptance Scenarios**:

1. **Given** a race completes (all runners finish obstacle 8), **When** the Results screen is shown, **Then** a race summary record is saved containing seed, tier, mode, timestamps, and all participant data.
2. **Given** a race summary is saved, **When** it is retrieved, **Then** every numeric field (distance, response time, XP) is consistent with what was shown on the Results screen.
3. **Given** two participants finish at exactly the same moment, **When** positions are assigned, **Then** the participant with the lower array index is ranked higher.

---

### Edge Cases

- What happens when the player submits after the per-obstacle timer expires? → Treated as Slow-correct tier (9 m) if the answer is correct; 0 m if incorrect.
- What happens when two runners finish the final obstacle simultaneously? → Lower array index wins the tiebreak.
- What happens when the player's browser tab loses focus mid-race? → The clock pauses; it resumes on tab focus.
- What happens when the player disconnects mid-race? → The race continues client-side; results are synchronised on reconnect.
- What happens in a Training race with only 1 participant? → No position indicator is shown; there are no opponent columns.
- What happens when the player answers obstacle 8 incorrectly? → 0 m movement; the race ends only after the problem is resolved (no infinite loop).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST enforce the state sequence: IDLE → LOBBY → COUNTDOWN → RACING → FINISHING → RESULTS.
- **FR-002**: The engine MUST reject all transitions not defined in the legal state machine; the state MUST remain unchanged on rejection.
- **FR-003**: The engine MUST calculate runner movement using the four response-time tiers: Perfect (< 2 s → 18 m), Excellent (2–4 s → 15 m), Good (4–6 s → 12 m), Slow (> 6 s → 9 m).
- **FR-004**: An incorrect answer MUST produce 0 m movement; runner distance MUST never decrease.
- **FR-005**: Each race MUST consist of exactly 8 obstacle problems.
- **FR-006**: The game clock MUST be monotonic, starting at the COUNTDOWN → RACING transition and ticking on each animation frame.
- **FR-007**: Per-obstacle timing MUST start when the problem card becomes visible and end when the player submits.
- **FR-008**: The game clock MUST pause when the browser tab loses focus and resume when focus is restored.
- **FR-009**: AI runner movement MUST be computed using: base response time for the tier + personality variance + Gaussian noise, then passed through the same movement-calculation function as the player.
- **FR-010**: AI runners MUST be updated sequentially per obstacle to prevent simultaneous visual movement.
- **FR-011**: Given the same seed and difficulty tier, an AI-only race MUST produce identical results on every replay.
- **FR-012**: The race seed MUST determine the problem sequence, AI variance samples, and initial positions.
- **FR-013**: The engine MUST transition to FINISHING as soon as any runner completes obstacle 8, and to RESULTS only after all runners have completed obstacle 8.
- **FR-014**: When two runners finish simultaneously, the one with the lower participant-array index MUST rank higher.
- **FR-015**: After every race, a summary record MUST be saved containing: race ID, seed, difficulty tier, mode, start timestamp, completion timestamp, and per-participant data (avatar ID, final position, problems correct, average response time in ms, total distance, XP earned).
- **FR-016**: In Training mode (single participant), position indicators and opponent columns MUST be hidden.

### Key Entities

- **Race**: A single contest identified by a UUID, associated with a seed, difficulty tier, mode, start/end timestamps, and a list of participants.
- **Participant**: A runner in the race — either the human player or an AI runner — with fields for avatar ID, position, problems correct, average response time, total distance, and XP earned.
- **Obstacle**: One of 8 sequential problem slots in a race; each has a start time (problem shown), an end time (answer submitted), correctness, and movement awarded.
- **AI Personality**: A configuration object per AI runner defining its response-time variance and base accuracy relative to the difficulty tier.
- **Race Seed**: A string value that initialises the pseudo-random sequences for problem selection, AI variance, and initial positions.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 8 obstacle problems appear in every completed race with no omissions or repeats within a single run.
- **SC-002**: Movement tier awarded per obstacle matches the observed response time in 100% of manual verification runs (no off-by-one in tier boundaries).
- **SC-003**: Replaying the same seed in Training mode produces identical problem sequences and AI distances across 10 consecutive replays.
- **SC-004**: Illegal state transitions are blocked in 100% of test attempts; the engine never enters an undefined state.
- **SC-005**: A race summary record is present and internally consistent for every completed race with no missing mandatory fields.
- **SC-006**: Per-obstacle clock pause/resume across tab-focus changes introduces no measurable timing error (timing accuracy within ± 50 ms of wall-clock elapsed time at moment of submission).
- **SC-007**: AI runners never visually overlap during movement updates across 20 consecutive race observations.

---

## Assumptions

- The race engine operates entirely client-side during an active race; no server calls are made while RACING state is active.
- "Monotonic" clock is implemented via `requestAnimationFrame` deltas accumulated in a variable, not via `Date.now()` directly, to avoid wall-clock drift.
- The difficulty tier is fixed for the duration of a race and does not change mid-race.
- XP calculation is handled by a separate system; the race engine only records the XP value it receives, not compute it.
- Reconnect synchronisation (after disconnect) is handled by a separate persistence layer; the race engine only produces the summary record.
- The maximum track distance per runner is 144 m (8 obstacles × 18 m Perfect tier); there is no bonus distance or overshoot mechanic.
- AI personality objects and their variance parameters are defined outside the race engine and injected at race initialisation.
- The spec does not address network multiplayer; all multi-participant races described here involve local AI runners only.
