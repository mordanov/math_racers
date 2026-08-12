# Feature Specification: Player Achievements

**Feature Branch**: `009-achievements`
**Created**: 2026-08-12
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - Earn an Achievement (Priority: P1)

A player completes a game action — finishing a race, reaching a level milestone, maintaining a problem-solving streak, or other qualifying activity — and automatically receives recognition for that accomplishment. The achievement is permanently recorded to their account.

**Why this priority**: This is the core mechanic. Without the ability to earn and permanently record achievements, there is no achievement system. All other stories depend on unlock records existing.

**Independent Test**: Can be fully tested by completing a qualifying game action and confirming the achievement appears in the player's unlocked list. Delivers value as a standalone persistence feature even without visual celebration.

**Acceptance Scenarios**:

1. **Given** a player has never completed a race, **When** they finish their first race, **Then** an achievement is recorded permanently in their account.
2. **Given** a player already holds an achievement, **When** the same qualifying condition is met again, **Then** no duplicate achievement is created.
3. **Given** two achievement conditions are met simultaneously in the same game event, **When** both triggers fire, **Then** both achievements are recorded.
4. **Given** the same game event is delivered more than once (duplicate delivery), **When** the system processes it again, **Then** no additional achievements are created.

---

### User Story 2 - Browse Achievements (Priority: P2)

A player can browse the full catalogue of available achievements and see which ones they have earned, when they earned them, and which remain locked. Hidden achievements are invisible until the player unlocks them.

**Why this priority**: Discovery and progress tracking are the engagement loop — players return to chase missing achievements only if they can see what's available. This turns a one-time unlock into a long-term retention driver.

**Independent Test**: Can be fully tested by querying the achievement catalogue and a specific player's unlock list, confirming unlocked items show title, description, icon and unlock date, and that hidden items are absent from locked listings.

**Acceptance Scenarios**:

1. **Given** a player has unlocked some achievements, **When** they view their achievement list, **Then** each unlocked achievement shows its title, description, icon, and the date it was earned.
2. **Given** a hidden achievement exists that the player has not unlocked, **When** they browse the achievement catalogue, **Then** the hidden achievement does not appear anywhere in the locked list.
3. **Given** a hidden achievement exists that the player has unlocked, **When** they view their achievements, **Then** the hidden achievement is visible with full title, description, and icon.
4. **Given** a player has never earned any achievements, **When** they browse the catalogue, **Then** the full list of non-hidden achievements is visible as locked entries.

---

### User Story 3 - Achievement Celebration (Priority: P3)

When a player earns a new achievement, they see a short animated celebration on the Results Screen. If they earn multiple achievements in one session, each is presented sequentially with a brief pause between them. No celebration interrupts an active race.

**Why this priority**: The celebration moment creates emotional resonance and reinforces the achievement loop. The system functions without it, but player delight and long-term retention depend on it.

**Independent Test**: Can be fully tested by triggering an achievement during a completed race and verifying the animation plays on the Results Screen after the race ends — not during the race itself.

**Acceptance Scenarios**:

1. **Given** a player earns an achievement, **When** the Results Screen appears, **Then** a badge animation plays (under 2 seconds total) accompanied by a visual effect and sound.
2. **Given** a player earns two achievements in one race, **When** the Results Screen appears, **Then** both animations play one after the other, separated by a 2-second pause — never simultaneously.
3. **Given** a player earns an achievement while a race is still active, **When** the race is ongoing, **Then** no achievement animation appears; the celebration is deferred until the Results Screen.
4. **Given** a player earns a hidden achievement, **When** the Results Screen shows the celebration, **Then** the achievement's title and description are revealed as part of the celebration.

---

### Edge Cases

- What happens when an achievement evaluation encounters an unexpected error? The failure is handled gracefully per achievement — other achievements in the same batch continue to evaluate and the player sees no error.
- What happens when a player is deleted? All their unlock records are removed along with the account; the achievement catalogue entries remain unchanged.
- What happens if an achievement catalogue entry is updated? Existing unlock records are unaffected; only future evaluations use the updated entry.
- What happens when a "meta achievement" (unlock N achievements) is triggered by another achievement unlock? The system re-evaluates relevant achievements after each unlock, allowing chains to resolve correctly.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST evaluate achievement eligibility automatically whenever a qualifying player action occurs: race completion, problem solved, level-up, avatar created, daily challenge completed, or achievement unlocked.
- **FR-002**: The system MUST permanently record each achievement unlock. Unlock records MUST NOT be deleted or modified after creation.
- **FR-003**: The system MUST prevent duplicate achievement unlocks. If a player already holds an achievement, re-evaluation of the same event MUST NOT create a second record.
- **FR-004**: Any player MUST be able to retrieve the full achievement catalogue. Hidden achievements MUST be excluded from this response for any player who has not unlocked them.
- **FR-005**: Any player MUST be able to retrieve their own list of unlocked achievements, including the unlock date for each.
- **FR-006**: Hidden achievements MUST NOT appear in the catalogue or in a player's locked achievement list before they are unlocked.
- **FR-007**: When multiple achievements are unlocked in the same game event, all MUST be recorded, and each MUST be presented in the celebration UI sequentially — never simultaneously — separated by a 2-second interval.
- **FR-008**: Achievement celebration animations MUST be deferred to the Results Screen when the player is in an active race at the time the achievement is earned.
- **FR-009**: Each individual achievement celebration animation MUST complete within 2 seconds.
- **FR-010**: Achievement evaluation failures MUST NOT be surfaced to the player as errors and MUST NOT prevent evaluation of other achievements in the same batch.
- **FR-011**: Achievement unlocks MUST be triggered exclusively by internal game events — there is no player-facing endpoint for directly granting achievements.

### Key Entities

- **Achievement (Catalogue Entry)**: A named accomplishment with a category, title, description, icon, and a hidden flag. The catalogue is static and managed by the development team; entries are never removed or renamed after release.
- **Player Achievement (Unlock Record)**: A permanent record linking a player to an earned achievement, including the unlock timestamp and an optional reference to the specific avatar involved (for avatar-specific achievements).

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of qualifying game actions result in achievement evaluation automatically — no manual trigger required.
- **SC-002**: Achievement unlock records are permanently preserved with zero records duplicated or lost under normal conditions.
- **SC-003**: Players can view their unlock list and the full catalogue within 1 second of opening the achievements section.
- **SC-004**: Each celebration animation completes in under 2 seconds; multiple sequential animations are separated by a 2-second pause.
- **SC-005**: Hidden achievements have a 0% appearance rate in catalogue or locked-list views for players who have not yet unlocked them.
- **SC-006**: Duplicate event delivery produces zero duplicate achievement records (idempotent unlock behaviour).

## Assumptions

- The achievement catalogue is maintained as a static, version-controlled list by the development team; players cannot create, modify, or delete achievements.
- Some achievements are tied to a specific avatar's performance (e.g., "Win 10 races with the same avatar"); the data model supports an optional avatar reference on unlock records.
- Achievement categories are: racing, mathematics, streaks, collection, social, milestones, exploration, and special.
- The celebration animation includes both a visual component (badge scale-in with sparkle particle effect) and an audio component (ascending chime notes and a short fanfare).
- The first version targets authenticated players, consistent with the existing XP Progression system.
- "Meta achievements" (e.g., "unlock N achievements") are supported — an achievement unlock can itself trigger further evaluation.
- Achievement icons are stored as static assets and referenced by path in the catalogue; icon management is out of scope for this feature.
