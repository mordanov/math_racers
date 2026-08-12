# Feature Specification: XP & Player Progression

**Feature Branch**: `008-xp-progression`  
**Created**: 2026-08-11  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Earn XP After a Race (Priority: P1)

After completing any race, the player automatically receives XP based on their performance — how many problems they answered correctly and whether they achieved a perfect-answer streak. The player can see their updated XP total and current level immediately on the results screen.

**Why this priority**: XP earning is the core engagement loop. Without it, progression has no input and the system has no purpose.

**Independent Test**: Submit a race result and verify the player's XP total increases by the correct calculated amount, level is recalculated, and level-up is detected when a boundary is crossed.

**Acceptance Scenarios**:

1. **Given** a player has completed a Quick Race with 7 correct answers out of 8 (longest streak = 5), **When** the race result is submitted, **Then** the player receives 240 XP: 100 (race completion) + 140 (7 × 20 correct answers) + 10 (1 streak bonus of 5 consecutive = 1 × 10) and their total XP is updated.
2. **Given** a player was at level 1 (360 XP), **When** they gain 240 XP bringing total to 600, **Then** their level is recalculated to 2 (`floor(sqrt(600/100))` = 2) and a level-up event is recorded.
3. **Given** a player submits a race result, **When** the same result is submitted again with the same idempotency key, **Then** XP is not re-awarded and the response returns the unchanged progression state.
4. **Given** a race result where `correct_answers` > `problems_solved`, **When** the result is submitted, **Then** the submission is rejected with a validation error.

---

### User Story 2 - View Current Progression (Priority: P2)

A player (or a parent viewing the dashboard) can look up the current XP total, level, and how much XP is needed to reach the next level at any time, without needing to submit a new race result.

**Why this priority**: Progression visibility is essential for motivation, but the read path depends on the write path being established first (P1).

**Independent Test**: After seeding a player with a known XP total, call the progression endpoint and verify the returned level, XP total, and XP-to-next-level values are all mathematically correct.

**Acceptance Scenarios**:

1. **Given** a player with 1,450 total XP, **When** their progression is retrieved, **Then** the response shows level 3, total_xp = 1450, and xp_to_next_level = 150 (next level 4 requires 1600 XP).
2. **Given** a player at exactly a level boundary (e.g., 900 XP = level 3), **When** progression is retrieved, **Then** xp_to_next_level equals the full XP gap to level 4, not 0.
3. **Given** a parent opens the dashboard for a child player, **When** the progression data is loaded, **Then** it shows the same level, XP, and next-level threshold as the player's own view.

---

### User Story 3 - Championship Race Bonus XP (Priority: P3)

Completing a race in championship mode awards a significant XP bonus on top of standard race XP. This incentivises players to participate in structured championship play.

**Why this priority**: Championship mode is a premium engagement layer. The bonus is a configuration detail on top of the already-working P1 XP system.

**Independent Test**: Submit a race result in championship mode and verify the 500-point mode bonus is added on top of the standard XP calculation.

**Acceptance Scenarios**:

1. **Given** a player completes a championship race with 5 correct answers and no streak, **When** the result is submitted with mode = championship, **Then** XP awarded = 100 + 100 + 500 = 700.
2. **Given** a player completes a quick race with identical stats, **When** mode = quick_race, **Then** XP awarded = 100 + 100 = 200 (no mode bonus).

---

### Edge Cases

- What happens when a player's level does not change after gaining XP (common case)? — Level-up event is NOT emitted; progression record is still updated.
- What happens when `correct_answers` > `problems_solved` in the submitted result? — Submission is rejected with a validation error.
- What happens if no races have been played yet? — Player progression starts at 0 XP, level 0; the next-level threshold is 100 XP.
- What happens when two race results for different races are submitted simultaneously? — Each is processed independently; XP is summed correctly.
- What if a daily challenge XP award arrives after a race result in the same session? — Both are recorded as separate events; the total is always the sum of all events.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST award XP to a player automatically when a race result is submitted successfully.
- **FR-002**: XP awarded per race MUST follow the formula: 100 (race completion) + (correct_answers × 20) + (floor(longest_streak / 5) × 10) + mode_bonus; where mode_bonus = 500 for championship mode and 0 otherwise.
- **FR-003**: System MUST recompute the player's current level using the formula `floor(sqrt(total_xp / 100))` after every XP award.
- **FR-004**: System MUST emit a level-up event whenever a player's level increases as a result of an XP award, including the previous level, new level, and total XP at the time of the event.
- **FR-005**: XP events MUST be append-only; existing XP event records MUST NOT be modified or deleted.
- **FR-006**: XP MUST never be deducted from a player's total.
- **FR-007**: Race result submission MUST be idempotent; submitting the same result twice (identified by idempotency key) MUST NOT award XP a second time and MUST return the unchanged progression state.
- **FR-008**: System MUST reject a race result where `correct_answers` is greater than `problems_solved` with a validation error.
- **FR-009**: System MUST expose a read endpoint returning a player's current level, total XP, and XP required to reach the next level.
- **FR-010**: The `xp_to_next_level` value returned MUST equal `xp_for_level(current_level + 1) − total_xp` and MUST never be negative.
- **FR-011**: Total XP shown in any response MUST always be derivable by summing all XP events recorded for that player.
- **FR-012**: All XP award and level update operations for a single race result MUST be atomic (succeed or fail together with no partial state).

### Key Entities

- **PlayerProgression**: Represents a player's running totals — current level, total XP accumulated, and when it was last updated.
- **XPEvent**: An immutable record of a single XP award — the source (race completion, correct answer, streak bonus, championship bonus), the amount, and optionally the race it relates to.
- **RaceResult**: The input that triggers XP calculation — includes correct answer count, longest streak length, mode, and an idempotency key to prevent duplicate processing.
- **LevelUpEvent**: A notification produced when a player crosses a level boundary — carries previous level, new level, and total XP at time of crossing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: XP is awarded within the same request-response cycle as race result submission — the player sees updated progression on the results screen without a separate reload.
- **SC-002**: 100% of race result submissions with valid data result in the correct XP amount being credited with no manual intervention.
- **SC-003**: Duplicate race result submissions (same idempotency key) never cause double XP awards — 0% duplication rate across all submissions.
- **SC-004**: Level calculation matches `floor(sqrt(total_xp / 100))` exactly for every player at every point in time — no rounding or formula drift.
- **SC-005**: Level-up events are produced for 100% of level-boundary crossings and never produced when no boundary is crossed.
- **SC-006**: Players can retrieve their current progression (level, XP, next-level threshold) within an acceptable response time under normal load.

## Assumptions

- The player identity and authentication system already exists; this feature consumes an authenticated player identifier and does not own account creation or login.
- Daily challenge XP is out of scope for this feature — it is a separate award path handled by a future endpoint.
- There is no XP cap or maximum level in this version; the formula handles arbitrarily large XP values.
- The frontend is responsible for presenting level-up animations and queuing level-up + achievement notifications in display order (level-up first, then achievement).
- Achievement unlocks triggered by level-up events are consumed by the achievement system, which is a separate feature and out of scope here.
- Problems solved count (`problems_solved`) is a required input field alongside `correct_answers` and is used solely for validation (correct_answers ≤ problems_solved).
- The race result endpoint already exists for recording race outcomes; XP award logic is being added to its response, not a new endpoint for race submission.
