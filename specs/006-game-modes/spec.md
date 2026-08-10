# Feature Specification: Game Modes

**Feature Branch**: `006-game-modes`
**Created**: 2026-08-10
**Status**: Draft
**Source**: docs/gameplay/spec-game-modes.md (FR-050–053; ADR-002; ADR-004)

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Complete a Quick Race (Priority: P1)

A player selects Quick Race, chooses the number of opponents and difficulty, and races against AI runners. When the race ends the player sees a result screen with their finishing position, XP earned, and correct/incorrect answer counts.

**Why this priority**: Core gameplay loop — everything else depends on being able to run a single race and record its outcome.

**Independent Test**: Launch a Quick Race with 3 opponents, finish the race, and verify the result screen appears with correct data.

**Acceptance Scenarios**:

1. **Given** a player with at least one avatar, **When** they start a Quick Race with 3 AI opponents, **Then** a race session is created and all runners appear on the track.
2. **Given** an active Quick Race, **When** the player crosses the finish line, **Then** the result screen shows finishing position, XP earned, correct answers, and mistake count.
3. **Given** a Quick Race result, **When** the result is submitted a second time with the same idempotency key, **Then** the server returns the original result and XP is not awarded again.

---

### User Story 2 — Run a Championship Series (Priority: P2)

A player starts a Championship, competes in a series of races (3–7), and accumulates points toward a final standings screen. If they close the browser mid-series, they can return and resume from the next unplayed race.

**Why this priority**: Championship is the primary long-form engagement loop; standings persistence is essential for player trust.

**Independent Test**: Start a 3-race Championship, complete Race 1, close the browser, reopen, and verify standings are preserved and Race 2 is available.

**Acceptance Scenarios**:

1. **Given** a player starts a 5-race Championship, **When** they complete Race 1, **Then** the standings update with points from Race 1 using the championship points table.
2. **Given** a Championship with 2 of 5 races complete, **When** the player closes and reopens the browser, **Then** the championship resumes from Race 3 with prior standings intact.
3. **Given** a Championship where the final race result is submitted, **When** the result is recorded, **Then** the championship status automatically transitions to `completed` and the final standings screen is shown.

---

### User Story 3 — Practice in Training Mode (Priority: P3)

A player enters Training mode and answers an infinite stream of problems at their own pace. There is no finish line. When they choose to exit, a partial result is saved recording how many problems they attempted.

**Why this priority**: Supports skill-building without competitive pressure; statistics must be recorded but no XP completion bonus is granted.

**Independent Test**: Start Training, answer 10 problems, exit voluntarily, and verify the session appears in Statistics with `finishing_position: null`.

**Acceptance Scenarios**:

1. **Given** a Training session is active, **When** the player answers problems, **Then** there is no finish line and the session continues indefinitely until the player exits.
2. **Given** a player exits Training voluntarily, **Then** a partial result is submitted with `finishing_position: null` and `problems_solved` equal to the number of checkpoints reached.
3. **Given** a partial Training result, **When** XP is calculated, **Then** per-correct-answer XP is awarded but no race-completion XP is granted.

---

### User Story 4 — Challenge a Matched Opponent in Duel (Priority: P3)

A player enters Duel mode and races against exactly one AI opponent whose difficulty tier matches the player's current adaptive tier.

**Why this priority**: Provides a focused head-to-head experience; tier-matching ensures the challenge is appropriately calibrated.

**Independent Test**: Start a Duel and confirm exactly 1 AI opponent appears on the track at the same difficulty tier as the player.

**Acceptance Scenarios**:

1. **Given** a player at difficulty tier 3, **When** they start a Duel, **Then** exactly one AI opponent at tier 3 (Balanced personality, tier_offset = 0) appears on the track.
2. **Given** a player at difficulty tier 1 (minimum), **When** they start a Duel, **Then** the opponent tier is clamped to tier 1 (never below 1).

---

### Edge Cases

- What happens when race setup is attempted with no avatars available? → Redirect to Avatar Creator; do not create a session.
- How does the system handle a duplicate result submission? → Return the original result via idempotency key; XP is not re-awarded.
- What if a Championship is interrupted after all races are played but status was not updated? → The final race result submission automatically transitions status to `completed`.
- What if Training is exited before answering any problems? → Submit a partial result with `problems_solved: 0`; no XP is awarded.
- What is the maximum number of opponents in a Quick Race? → Up to 4 AI opponents (player + 4 = 5 total runners, per FR-021).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support four race modes: Quick Race, Championship, Training, and Duel.
- **FR-002**: The system MUST prevent race session creation when the player has no avatar; the player MUST be redirected to Avatar Creator.
- **FR-003**: Quick Race MUST create a single race session, run one race, and submit the result immediately on finish.
- **FR-004**: Championship MUST create a persistent championship state tracking points, podiums, and standings across all races in the series.
- **FR-005**: Championship series length MUST be configurable between 3 and 7 races.
- **FR-006**: Championship standings MUST be preserved across browser sessions until the championship is marked `completed`.
- **FR-007**: Championship status MUST automatically transition to `completed` when the final race result is submitted.
- **FR-008**: Championship points MUST be awarded per finishing position: 1st → 10 pts, 2nd → 6 pts, 3rd → 3 pts, 4th → 1 pt, 5th → 0 pts.
- **FR-009**: Training MUST run without a finish line; the session continues until the player exits voluntarily.
- **FR-010**: Training MUST submit a partial result on exit with `finishing_position: null`; no race-completion XP is awarded.
- **FR-011**: Per-correct-answer XP MUST still be awarded in Training.
- **FR-012**: Duel MUST create exactly one AI opponent matched to the player's current adaptive difficulty tier (tier_offset = 0, Balanced personality).
- **FR-013**: Duel opponent tier MUST be clamped to a minimum of tier 1.
- **FR-014**: Result submission MUST be idempotent; a client-supplied idempotency key MUST prevent duplicate XP awards on retry.
- **FR-015**: Race sessions MUST be initialised with a server-generated seed for deterministic problem generation.

### Key Entities

- **RaceSession**: Represents a single race instance; holds mode, opponent count, difficulty tier, seed, and lifecycle status (`pending | active | completed | abandoned`).
- **RaceResult**: Records a player's race outcome including finishing position, problems solved, correct answers, mistakes, distance, duration, XP earned, and idempotency key.
- **ChampionshipState**: Tracks a multi-race series including total races, races completed, per-participant standings (points, podiums, position), and series status (`active | completed`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A player can start and complete a Quick Race in a single session with results displayed immediately on finish.
- **SC-002**: Championship standings are preserved correctly across browser sessions for 100% of interrupted championships.
- **SC-003**: Submitting the same race result twice with the same idempotency key never results in duplicate XP — verified across 100% of tested cases.
- **SC-004**: Training sessions record partial statistics on every voluntary exit, with no missed sessions.
- **SC-005**: Duel always presents exactly one AI opponent; opponent tier matches the player's current tier in 100% of cases (minimum tier 1).
- **SC-006**: Race setup blocks session creation when no avatar exists, redirecting the player to Avatar Creator 100% of the time.
- **SC-007**: Championship auto-completes (status → `completed`) on final race result submission without manual intervention.

## Assumptions

- All four modes are accessible from the same Race Setup entry point; mode selection happens before session creation.
- The player's current adaptive difficulty tier is available at race setup time and does not change mid-race.
- "Runner count" in FR-021 refers to total runners including the player (so 5 total = player + 4 AI opponents).
- Quick Race supports 1–5 total runners; the player counts as one, so 0–4 AI opponents.
- Championship interrupted mid-series is resumable only within the same player session scope (not cross-device).
- Seed collisions are negligible and require no collision detection (server-generated 64-bit integers).
- Training mode does not contribute to Championship standings or ranking metrics.
