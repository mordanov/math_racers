# Feature Specification: Race Experience Improvements

**Feature Branch**: `016-race-experience`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: User description: Improve race pacing with a configurable time setting; make tier 3–5 math questions a reasonable mental-arithmetic challenge; prevent trivial self-division from dominating division sets; fix championship result recording and completion; show moving player avatars on the track; and add separate sound-effects and music volume controls.

## User Scenarios & Testing

### User Story 1 - Give the child enough time to calculate (Priority: P1)

A parent can change the amount of time available during a race so a child can read and solve each math problem without the race ending too quickly.

**Why this priority**: The current pace prevents the child from completing the intended mental calculation.

**Independent Test**: Change the time setting, start a new race, and verify that its timer follows the selected duration while an already-running race remains unchanged.

**Acceptance Scenarios**:

1. **Given** the parent has selected a per-problem time limit, **When** a new race starts, **Then** each problem receives that amount of time.
2. **Given** a timed race is already in progress, **When** the parent changes the saved setting, **Then** the active race keeps its original timing and the next timed race uses the new value.
3. **Given** the timer reaches its configured limit before an answer is submitted, **When** the round ends, **Then** the unanswered problem is recorded as a timeout with no race progress and the next problem is shown.
4. **Given** no saved value exists, **When** a race starts, **Then** the 30-second default is used.
5. **Given** Training mode is active, **When** a problem is displayed, **Then** no round timer is enforced.
6. **Given** the browser tab loses focus during a competitive race, **When** the tab is hidden, **Then** the problem timer pauses with the existing race clock and resumes when the tab is active again.

### User Story 2 - Practice appropriately challenging arithmetic (Priority: P1)

A child playing difficulty tiers 3, 4, or 5 receives problems that are neither trivial single-digit additions nor impractical two-digit-by-two-digit multiplication.

**Why this priority**: Problems should exercise the intended skill while remaining feasible to calculate mentally within the available time.

**Independent Test**: Generate fixed-seed problem sets for tiers 3–5 and verify every problem matches the tier's allowed operation and operand ranges.

**Acceptance Scenarios**:

1. **Given** tier 3 is selected, **When** a multiplication problem is generated, **Then** it multiplies a two-digit number by a one-digit number.
2. **Given** tier 4 is selected, **When** a division problem is generated, **Then** it is exact, uses a one-digit divisor, and has a quotient greater than one.
3. **Given** tier 5 is selected, **When** a mixed problem is generated, **Then** addition uses two two-digit operands, multiplication uses a two-digit and a one-digit operand, and division follows the tier 4 constraints.
4. **Given** a fixed tier and seed, **When** the problem set is regenerated, **Then** the same problems appear in the same order.
5. **Given** Tier 6 includes division, **When** the saved operand range cannot produce any exact division with a quotient greater than one, **Then** the invalid settings are rejected before a race starts.

### User Story 3 - Complete a championship and keep its results (Priority: P1)

A child can finish each championship race, see standings advance, resume an interrupted championship, and see the championship marked complete after the final race.

**Why this priority**: Championship progress is unusable if race results are discarded or the final state is never reached.

**Independent Test**: Complete a multi-race championship, reload the application between races, and verify persisted race results, standings, and final completion.

**Acceptance Scenarios**:

1. **Given** an active championship race finishes, **When** its result is submitted, **Then** that result is persisted and championship standings and completed-race count are updated.
2. **Given** a result submission is retried, **When** the same race result is received again, **Then** it is not counted or awarded twice.
3. **Given** the browser is closed after a non-final race, **When** the child returns, **Then** the championship resumes at the next unplayed race with prior standings intact.
4. **Given** the final scheduled race is recorded, **When** the child opens championship results, **Then** final standings are available and the championship is marked complete.

### User Story 4 - See their avatar racing (Priority: P2)

A child sees the selected avatar moving along the race track instead of an abstract marker, making race progress easier to follow.

**Why this priority**: The avatar makes the central race action more personal and visually understandable.

**Independent Test**: Start a race with a selected avatar, answer problems that change progress, and verify that the avatar image remains associated with the player and moves to the corresponding track position.

**Acceptance Scenarios**:

1. **Given** a race has started, **When** the race screen renders the player, **Then** it shows the selected avatar portrait on the player's track.
2. **Given** the player's race progress changes, **When** the screen updates, **Then** the portrait moves smoothly to the new position without changing the recorded race distance.
3. **Given** reduced motion is enabled, **When** race progress changes, **Then** the avatar position updates without non-essential movement animation.
4. **Given** no portrait image can be loaded, **When** the race screen renders, **Then** it shows an existing safe fallback and the race remains playable.

### User Story 5 - Adjust music and sound effects separately (Priority: P2)

A parent or child can independently change background-music and sound-effects volume, including muting either one without muting the other.

**Why this priority**: Families need control over different audio layers without disabling all game feedback.

**Independent Test**: Change each control independently, trigger music and a sound effect, and verify that each follows its own saved level after navigating away and returning.

**Acceptance Scenarios**:

1. **Given** the settings screen is open, **When** the user changes music volume, **Then** background music changes immediately and sound-effect volume does not.
2. **Given** the settings screen is open, **When** the user changes sound-effects volume, **Then** effects change immediately and music volume does not.
3. **Given** either volume is set to zero, **When** that audio category plays, **Then** it is silent while the other category remains at its chosen level.
4. **Given** the application is reloaded, **When** saved settings are restored, **Then** both independent volume levels are preserved.

### Edge Cases

- A saved race-time value is missing or outside the supported range.
- A timer expires while an answer is being submitted or the browser tab is backgrounded.
- A generated problem set has a fixed seed and a small requested count.
- Division generation cannot use a divisor that would produce a quotient greater than one.
- A championship result is submitted more than once or after the championship is already complete.
- The selected avatar image is missing, unavailable offline, or has not finished loading.
- Audio settings are unavailable because browser storage is blocked or audio playback is unsupported.
- Reduced-motion preference changes while a race is active.

## Requirements

### Functional Requirements

- **FR-001**: The parent MUST be able to configure the time limit for each competitive math problem from 10 to 60 seconds in 5-second increments; the default MUST be 30 seconds.
- **FR-002**: The selected timing setting MUST be saved and applied to newly started competitive races; changing it MUST NOT alter an active race. Training mode MUST remain untimed.
- **FR-003**: When a problem's time limit expires without an answer, the system MUST record a timeout with no progress for that problem and advance to the next problem without losing prior answers.
- **FR-004**: Tier 3 multiplication problems MUST use a two-digit number multiplied by a one-digit number.
- **FR-005**: Tier 4 division problems MUST have integer results, use a one-digit divisor, and have a quotient greater than one.
- **FR-006**: Tier 5 addition problems MUST add two two-digit numbers; tier 5 multiplication and division MUST follow the operand constraints defined for tiers 3 and 4.
- **FR-007**: Tiers 3–5 MUST NOT generate single-digit-plus-single-digit problems or two-digit-by-two-digit multiplication problems.
- **FR-008**: The system MUST generate no self-division problems (`n ÷ n`) in any division problem set, including Tier 6, keeping their frequency below the requested 0.5% maximum. Tier 6 settings that cannot generate any exact division with a quotient greater than one MUST be rejected before a race starts.
- **FR-009**: Repeating problem generation with the same tier and seed MUST preserve deterministic ordering and results.
- **FR-010**: When a championship race completes, the system MUST persist its result, update standings, and advance the championship to the next unplayed race.
- **FR-011**: Championship result handling MUST be idempotent; retries MUST NOT duplicate a race, points, or awards.
- **FR-012**: Recording the final scheduled race MUST persist the final standings and transition the championship to completed.
- **FR-013**: The race screen MUST represent every participant with avatar imagery and move each image according to that participant's existing race progress. The human participant MUST use the selected avatar; opponents MAY use portraits from the shared published-avatar catalog or a distinct built-in avatar fallback. Private child-profile portraits MUST NOT be exposed as opponents.
- **FR-014**: Avatar movement MUST respect the application's reduced-motion preference and retain a usable fallback when the image is unavailable.
- **FR-015**: The settings screen MUST provide independent, persistent music and sound-effects volume controls.
- **FR-016**: Changing an audio volume MUST apply immediately to its own audio category and MUST NOT change the other category.
- **FR-017**: Setting either audio category to zero MUST mute only that category.
- **FR-018**: The authenticated shared avatar catalog MUST include only portrait URLs for published avatars with an active portrait; it MUST NOT expose avatar names, account IDs, child-profile IDs, or other profile data.

### Key Entities

- **Race timing preference**: The selected duration behavior used by newly created race rounds.
- **Math problem**: An operation, its operands, answer, tier, and deterministic generation seed.
- **Championship result**: A persisted race outcome associated with one scheduled championship race and its resulting standings.
- **Racer presentation**: The participant's avatar image, track position, and motion preference during a race.
- **Audio preferences**: Independent music and sound-effects levels retained between visits.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A parent can select a per-problem time limit from 10–60 seconds in 5-second increments and observe the 30-second default or selected value applied on the next race without a page reload.
- **SC-002**: In a deterministic sample of 1,000 generated tier 3–5 problems, every operand pattern follows its tier constraints; none is a prohibited trivial addition or two-digit-by-two-digit multiplication.
- **SC-003**: Across 10,000 generated division problems, zero are self-division problems and all answers are exact.
- **SC-004**: A championship can be completed through its final scheduled race, with each result and the final standings still present after reloading the application.
- **SC-005**: The player's avatar visibly changes track position after progress changes, while reduced-motion mode suppresses non-essential movement animation.
- **SC-006**: Music and sound-effects volume can be adjusted independently from 0% to 100%, and each value remains effective after navigation and reload.
- **SC-007**: A Tier 6 configuration that includes division but cannot produce an exact result with quotient greater than one is rejected before race start; valid Tier 6 divisions never use quotient one.

## Assumptions

- The application continues to use the existing six difficulty tiers, race modes, championship rules, selected avatars, and audio assets.
- A parent-facing settings surface is appropriate for the race timing control; the saved value applies to newly started races for the active player.
- A race round is one math problem in competitive modes. If its 10–60 second limit expires without an answer, the timeout counts as unanswered, awards no progress, and advances to the next problem. Training remains unlimited and untimed.
- A safe avatar fallback already used elsewhere in the application can be reused; no new generated artwork is required.
- The 0.5% self-division limit is satisfied by excluding self-division entirely across all tiers.
- Tier 3–5 operand-width limits improve mental-arithmetic suitability without changing tiers 1 and 2. Tier 6 retains parent-selected operations/ranges, but division must have quotient greater than one and incompatible ranges are rejected.
- The existing separate music and sound-effect volume controls remain in Settings; the requested work ensures that saved values apply immediately and consistently during playback rather than adding duplicate controls.
- Existing browser preference persistence is acceptable for audio controls unless current product rules require account-synchronized preferences.
- A competitive problem timer pauses and resumes with the existing race clock while the browser tab is unfocused.
- Opponent portraits come only from the shared published-avatar catalog already available to the application; private child-profile portraits are never fetched or exposed for this feature.

## Manual Verification Steps

1. In Settings, choose 45 seconds per problem, start a competitive race, and
   confirm each of its eight problems uses 45 seconds. Change the setting during
   the race and confirm only the next race uses the new value.
2. Hide the browser tab during a timed problem and confirm the timer pauses;
   return to the tab and confirm it resumes. Start Training and leave a problem
   open longer than 60 seconds; confirm it remains available and no timeout is
   submitted. In a timed race, allow a problem to expire and confirm its
   ordered empty answer is saved once, awards no movement, and the next problem
   appears.
3. Generate seeded samples for tiers 3, 4, and 5. Confirm tier 3 multiplication
   is two-digit by one-digit, tier 4 division is exact with a one-digit divisor
   and quotient greater than one, and tier 5 addition uses two two-digit
   operands. Repeat each seed and compare problem order.
4. Complete all races in a championship, reloading between races. Confirm each
   result changes standings once, resuming opens the next race, and the final
   result marks the championship complete.
5. Start a race with a selected player portrait and opponents. Confirm each
   participant has a selected, shared-published, or fallback image (never a
   private portrait from another child profile), images move with progress,
   and reduced-motion mode suppresses movement animation.
6. Change music volume while music is playing and SFX volume while triggering
   effects. Confirm each changes immediately without affecting the other,
   persists after navigation/reload, and setting one to zero leaves the other
   audible.
