# Feature Specification: Avatar Generation

**Feature Branch**: `007-avatar-generation`
**Created**: 2026-08-10
**Status**: Draft
**Input**: Avatar creation flow — child customises a character; the system generates a named, personalised portrait.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Create a New Avatar (Priority: P1)

A child selects their character's species, colours, hairstyle, and optional accessories, then submits the form. The system generates a unique, personalised portrait and displays it in the child's avatar gallery within 30 seconds.

**Why this priority**: This is the core value of the feature. Without a successful creation flow, nothing else functions. Every other story depends on at least one avatar existing.

**Independent Test**: Complete the avatar creation form with a species and default settings. Confirm that a portrait appears in the gallery and the avatar has a generated name and personality.

**Acceptance Scenarios**:

1. **Given** a child with no avatars, **When** they complete the creation form and submit, **Then** a portrait appears in the gallery within 30 seconds with a generated name, personality blurb, and biography.
2. **Given** a child submits the form with only species selected, **When** the system processes the request, **Then** sensible defaults fill all other fields and generation completes successfully.
3. **Given** generation is taking longer than expected, **When** the child checks the gallery, **Then** a progress indicator is visible and the portrait appears once ready.

---

### User Story 2 — Regenerate a Portrait (Priority: P2)

A child who dislikes their avatar's current portrait can request a new version. The system produces a new image while keeping all character metadata (name, personality, biography) and the previous portrait version intact.

**Why this priority**: Children will want to retry if they don't like the first result. Locking them to one image per avatar reduces engagement. This story depends only on US1 (an avatar must exist).

**Independent Test**: Generate an avatar, then click Regenerate. Confirm a new portrait appears and the original is still accessible in portrait history.

**Acceptance Scenarios**:

1. **Given** an existing avatar, **When** the child clicks Regenerate, **Then** a new portrait is produced and displayed; the name, personality, and biography remain unchanged.
2. **Given** a regeneration request, **When** the system generates the new portrait, **Then** both the new and original portrait are accessible (portrait history is preserved; no version is deleted).

---

### User Story 3 — Manage Existing Avatars (Priority: P3)

A child can rename their avatar, mark one avatar as their favourite, and delete avatars they no longer want. The gallery reflects these changes immediately.

**Why this priority**: Gallery management is important for long-term engagement but not required for first use. It depends on US1.

**Independent Test**: Rename an avatar, set it as favourite, then delete a different avatar. Confirm all three actions reflect immediately in the gallery.

**Acceptance Scenarios**:

1. **Given** an existing avatar, **When** the child renames it, **Then** the new name appears in the gallery immediately.
2. **Given** multiple avatars, **When** the child marks one as favourite, **Then** that avatar is highlighted/pinned in the gallery.
3. **Given** an existing avatar, **When** the child deletes it, **Then** it is removed from the gallery and the slot becomes available.
4. **Given** a child with 50 avatars (the maximum), **When** they attempt to create a 51st, **Then** they see a friendly message explaining the limit and no generation is attempted.

---

### Edge Cases

- What happens when generation fails after all retry attempts? → Child sees a friendly error with an option to try again manually.
- What happens when the child closes the browser during generation? → Generation continues server-side; the portrait appears in the gallery on next visit.
- What happens when an invalid colour value is submitted? → The system sanitises it or rejects it with a clear error; no generation is attempted with unsafe input.
- What happens when the generation service is unavailable? → Child sees a friendly error; the failed job does not silently disappear.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A child MUST be able to create a new avatar by selecting species, colours, hairstyle, and optional accessories.
- **FR-002**: The system MUST generate a unique name, personality, biography, and portrait for each avatar based on the child's selections.
- **FR-003**: Portrait generation MUST complete within 30 seconds under normal conditions.
- **FR-004**: The system MUST display a progress indicator while generation is in progress.
- **FR-005**: If generation fails, the system MUST retry automatically up to 3 times before surfacing a friendly error to the child.
- **FR-006**: A child MUST be able to regenerate a new portrait for an existing avatar without losing the avatar's name or personality.
- **FR-007**: All portrait versions for an avatar MUST be preserved and accessible (no version is deleted on regeneration).
- **FR-008**: A child MUST be able to rename an avatar at any time.
- **FR-009**: A child MUST be able to mark one avatar as their favourite.
- **FR-010**: A child MUST be able to delete an avatar they own.
- **FR-011**: The system MUST enforce a maximum of 50 avatars per child profile; attempts beyond this limit MUST be rejected with a clear message.
- **FR-012**: The system MUST allow at most 2 concurrent generation jobs per account.
- **FR-013**: The system MUST limit avatar generation to 10 attempts per account per hour.
- **FR-014**: Generated portraits MUST pass technical quality checks (correct dimensions, valid image, non-empty); failed checks trigger the retry strategy.
- **FR-015**: A child who closes the browser mid-generation MUST find the completed portrait in their gallery on return.

### Key Entities

- **Avatar**: A named character owned by a child profile. Has species, colours, hairstyle, accessories, generated metadata (name, personality, biography), and one or more portrait versions.
- **Portrait**: An image associated with an avatar. One portrait is current; previous versions are preserved in history.
- **GenerationJob**: A background task that tracks the lifecycle of a single portrait creation or regeneration attempt (queued → processing → complete or failed).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A child can create an avatar and see the finished portrait within 30 seconds on a standard connection.
- **SC-002**: At least 95% of generation attempts complete successfully (without reaching the failed state after all retries).
- **SC-003**: A child who closes the browser during generation loses no work — the portrait appears in the gallery on next visit in 100% of cases.
- **SC-004**: The gallery correctly enforces the 50-avatar limit; the 51st creation attempt is blocked with a clear, friendly message every time.
- **SC-005**: A child can complete the full avatar creation flow (form → portrait in gallery) without requiring any help or support.

---

## Assumptions

- Children are the primary actors; parental/guardian accounts exist but avatar management is performed by the child.
- The child already has an active child profile before entering the avatar creation flow.
- The creation form requires only species to submit; all other fields have sensible defaults.
- Portrait history is unlimited per avatar (every generated version is retained).
- Concurrent generation limits (2 per account, 10 per hour) apply at the account level, not the child-profile level.
- The avatar gallery is the entry point for race setup; an avatar must exist before a race can be started (enforced in the Race Setup flow, not here).
