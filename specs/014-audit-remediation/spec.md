# Feature Specification: Audit Remediation

**Feature Branch**: `014-audit-remediation`  
**Created**: 2026-10-10  
**Status**: Ready for planning  
**Input**: User description: "Implement the remediation actions in the Math Racers architecture audit."

## User Scenarios & Testing

### User Story 1 - Complete a race and keep correct results (Priority: P1)

A child starts a race, completes it, and sees a result that belongs to that
child. A repeated result submission does not give extra rewards or change the
result.

**Why this priority**: The race setup and result flow is a critical game path.

**Independent Test**: Start a race, complete it, then submit the same result
again. Confirm the child receives one result and one set of rewards.

**Acceptance Scenarios**:

1. **Given** a child has selected a valid avatar, **When** the child starts a
   race, **Then** the game creates a session with the selected mode and settings.
2. **Given** the race includes AI opponents, **When** the child submits the
   result, **Then** the result, rewards, and statistics belong to the human
   participant and not to the winner by rank.
3. **Given** the result has already been saved, **When** the same result is
   submitted again, **Then** the game returns the saved result and does not add
   another reward or statistic update.
4. **Given** a championship race ends, **When** the standings update, **Then**
   points follow the approved table: 10, 8, 6, 4, 2 for first through fifth
   place.

### User Story 2 - Keep each child's data separate (Priority: P1)

A parent selects a child and can view, export, or delete that child's data.
Children in one family cannot see or change each other's data.

**Why this priority**: Child data privacy and parent control are required.

**Independent Test**: Create two child profiles. Create data for each profile.
Try to read, change, export, and delete the other child's data.

**Acceptance Scenarios**:

1. **Given** two child profiles belong to one parent, **When** one child opens
   their data, **Then** only that child's data is available.
2. **Given** a parent requests data for a child, **When** the parent is
   authorised, **Then** export and deletion apply only to the selected child.
3. **Given** existing records belong only to a parent account, **When** the
   system migrates them, **Then** children cannot access the records until the
   parent assigns their owner. The system does not divide or copy records.

### User Story 3 - Use Training and progression rules (Priority: P1)

A child can practise without opponents or time pressure. Training continues
until the child exits. Correct answers earn the approved answer reward. Training
does not earn a race-completion reward.

**Why this priority**: Training must support practice without competitive
pressure and must use one approved reward rule.

**Independent Test**: Start Training, answer more than eight problems, exit, and
check the saved session and rewards.

**Acceptance Scenarios**:

1. **Given** a child starts Training, **When** the child keeps practising,
   **Then** the session continues without a finish line, timer, or opponent.
2. **Given** a child answers a problem correctly in Training, **When** the
   answer is saved, **Then** the child receives the approved correct-answer XP.
3. **Given** a child exits Training, **When** the session is saved, **Then** no
   race-completion XP is awarded.
4. **Given** a child's XP is zero, **When** the game shows the child's level,
   **Then** the child is Level 1.
5. **Given** a parent selects a difficulty tier, **When** the child starts a
   session, **Then** Tiers 3 and 4 use multiplication and division,
   respectively. A custom Tier 6 uses the parent's saved settings.

### User Story 4 - See accurate learning progress (Priority: P1)

A child and parent see statistics that reflect the child's answers and
operations. Released achievements unlock when their documented conditions are
met.

**Why this priority**: Progress reports must support learning, not show
incorrect or missing results.

**Independent Test**: Complete problems from each operation and trigger released
achievement conditions. Compare the displayed summary with the saved answers.

**Acceptance Scenarios**:

1. **Given** a child has answered problems in more than one operation, **When**
   a parent opens the summary, **Then** strongest and weakest operations match
   the saved answers.
2. **Given** a child has answered problems in more than one operation, **When**
   the child opens statistics, **Then** favourite operation matches the most
   played operation.
3. **Given** a released achievement condition is met, **When** the related play
   event is saved, **Then** the achievement unlocks once.

### User Story 5 - Use safe avatar generation (Priority: P1)

A child sees only an image that passes the required technical and child-safety
checks. If a required check fails, the image is not published.

**Why this priority**: Children must not receive images that fail the approved
content rules.

**Independent Test**: Submit valid and invalid generated images. Confirm that
only images that pass every blocking check become visible.

**Acceptance Scenarios**:

1. **Given** an image passes all required checks, **When** generation finishes,
   **Then** the image can become available to the child.
2. **Given** an image fails a required check, **When** generation finishes,
   **Then** the image stays unavailable and the child receives a safe message.
3. **Given** a provider or storage service changes, **When** the generation
   flow runs, **Then** product behaviour does not change.

### User Story 6 - Practise with cached data while offline (Priority: P2)

A child can start and finish Training without a network connection when the
child's required data is already cached. The game syncs saved results when the
connection returns.

**Why this priority**: Offline access is a documented requirement and supports
reliable practice.

**Independent Test**: Load child data online, disconnect the network, complete a
Training session, reconnect, and confirm the result syncs once.

**Acceptance Scenarios**:

1. **Given** the child's avatar data is cached, **When** the child opens
   Training offline, **Then** the game does not require an avatar-list request.
2. **Given** a Training result is saved offline, **When** the network returns,
   **Then** the result syncs once and does not create duplicate rewards.

## Edge Cases

- A child submits the same race result more than once.
- The result lists an AI participant before the human participant.
- A parent selects a child profile that belongs to another account.
- A parent has not assigned legacy account records to a child.
- A Training session ends before the first answer or during an answer.
- A Tier 6 session has no saved custom settings.
- Two answers tie for strongest or weakest operation.
- An achievement event is delivered more than once.
- An image safety check or external image service is unavailable.
- A child goes offline before data is cached or while a result is syncing.
- A migration fails after some records have been assigned.
- The daily challenge is not included in v1.0.

## Requirements

### Functional Requirements

- **FR-001**: The game MUST create a race session before it saves the race result.
- **FR-002**: A race result MUST identify the human participant. The game MUST
  NOT infer the human from rank or list order.
- **FR-003**: Repeating a saved result MUST NOT create another race, reward,
  statistic update, or achievement unlock.
- **FR-004**: Each child profile MUST own its avatars, race results, progression,
  statistics, and achievements.
- **FR-005**: The system MUST check parent and child ownership before it reads,
  changes, exports, or deletes child data.
- **FR-006**: The system MUST require a parent to assign existing account-owned
  records before children can access them. It MUST NOT guess or split their
  ownership.
- **FR-007**: Race results, rewards, statistics, and achievements MUST remain
  consistent if a save fails or is repeated.
- **FR-008**: Training MUST continue until the child exits. It MUST have no
  opponent, timer, or finish line. It MUST award XP for correct answers and no
  race-completion XP.
- **FR-009**: Championship points MUST be 10, 8, 6, 4, and 2 for first through
  fifth place. A completed championship MUST award +500 XP once.
- **FR-010**: Tier 3 MUST use multiplication. Tier 4 MUST use division. Tier 6
  MUST use the parent's saved custom settings.
- **FR-011**: Statistics MUST show the strongest, weakest, and favourite
  operations from recorded answers.
- **FR-012**: Each released achievement MUST have a tested condition. An
  achievement MUST unlock no more than once for the same condition.
- **FR-013**: An image MUST pass all required technical and child-safety checks
  before it becomes visible to a child. Failed or unavailable checks MUST block
  publication.
- **FR-014**: State-changing actions MUST have CSRF protection. Login,
  registration, and avatar generation MUST have rate limits.
- **FR-015**: When required child data is cached, the child MUST be able to start
  and finish Training offline. Offline results MUST sync once when the network
  returns.
- **FR-016**: AI and object storage services MUST be replaceable without changes
  to product behaviour.
- **FR-017**: Domain rules MUST not be implemented in API route handlers.
  Cross-domain race-result work MUST use an application-level flow and explicit
  events.
- **FR-018**: Daily Challenge MUST remain outside v1.0. The system MUST NOT
  award daily-challenge XP until the feature is approved for a release.

### Key Entities

- **Parent account**: The adult who manages child profiles.
- **Child profile**: A child identity that owns play data under a parent account.
- **Race session and result**: A play attempt and its saved outcome.
- **Progress record**: XP, level, and reward history for a child.
- **Operation answer**: A child's answer, operation, and correctness.
- **Achievement**: A released goal and its unlock state for a child.
- **Avatar asset**: A generated image and the checks that allow or block release.
- **Offline result**: A locally saved result that is waiting to sync.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All race setup and result scenarios pass contract and integration
  tests.
- **SC-002**: Repeating a race result creates zero duplicate rewards or
  statistics.
- **SC-003**: In all ownership tests, a child receives no data owned by another
  child.
- **SC-004**: Training supports more than eight answers and continues until the
  child exits.
- **SC-005**: Every released achievement has at least one passing trigger test.
- **SC-006**: No image that fails a required check becomes visible to a child.
- **SC-007**: A cached child can finish Training offline and sync the result
  once.
- **SC-008**: The project records results for startup under 3 seconds, race
  loading under 2 seconds, and problem generation under 1 millisecond in the
  target test environment.
- **SC-009**: The team records backup and restore results and accessibility
  checks before release.

## Manual Verification Steps

1. Create a parent account and two child profiles. Create an avatar and complete
   a race for each child.
2. Try to view, change, export, and delete each child's data while the other
   child is selected. Confirm the data remains separate.
3. Start Training. Answer more than eight problems. Confirm there is no timer,
   opponent, or finish line. Exit and check the XP award.
4. Complete a championship. Check the points for each place and the one-time
   championship XP award.
5. Submit the same result twice. Confirm the game shows one saved result and
   one set of rewards.
6. Use a generated image that fails a required safety check. Confirm it is not
   visible to a child.
7. Cache child data, disconnect the network, complete Training, reconnect, and
   confirm one result sync.
8. Use keyboard navigation and a screen reader on the changed screens. Check
   colour contrast and reduced-motion behaviour.

## Assumptions

- The approved championship points are 10, 8, 6, 4, 2. The parent owner of the
  requirements can change this table only by updating the source and derived
  requirements first.
- Tiers 3 and 4 use multiplication and division, as defined in the source
  economy specification.
- Correct answers in Training earn the normal correct-answer XP. Training does
  not earn race-completion XP.
- Level 1 starts at 0 XP.
- Image validation is automatic. Parental approval is not required in v1.0.
- Daily Challenge is a future feature and is not part of v1.0.
- A parent must assign each legacy record to a child before that child can
  access it. The migration must not infer an owner.
- The implementation uses the existing modular monolith and adds no general
  event platform.
