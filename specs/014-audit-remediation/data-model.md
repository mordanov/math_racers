# Data Model: Audit Remediation

## Ownership rule

Child-owned records keep `account_id` for parent authorisation and gain
`child_profile_id`. New records require a valid child profile. Legacy records
may have a null child profile until the parent assigns an owner. Child-facing
queries must exclude null-owner records.

## Entities

| Entity | Ownership and fields | Rules |
|---|---|---|
| ChildProfile | `id`, `account_id`, display name | The authenticated parent owns the profile. |
| Avatar | Existing avatar fields, `account_id`, nullable legacy `child_profile_id` | New avatars require a child profile. Generation limits apply per account and per child as documented. |
| Race | Session fields, `account_id`, `child_profile_id`, `avatar_id`, mode, tier, seed, status, timestamps, idempotency key | One session has one child, one selected human avatar, and at most one result. |
| RaceParticipant | Race ID, avatar ID, position, answer totals, operation answers | The server identifies the human from the race session, not rank. |
| OperationAnswer | Race ID, operation, correctness, response time | Used to calculate operation statistics. |
| PlayerProgression | Account ID, nullable child profile ID, XP, level | One unassigned legacy row may exist per account. Assigned rows are unique per child. |
| XPEvent | Account ID, nullable child profile ID, source, amount, race ID | Append-only. Result processing is idempotent. |
| PlayerStats | Account ID, nullable child profile ID, totals | Derived from owned race sessions and operation answers. |
| AvatarStats | Account ID, nullable child profile ID, avatar ID, totals | Scoped to the avatar's selected child. |
| RaceSession history | Account ID, nullable child profile ID, avatar ID, race ID, aggregates and timestamps | Historical rows remain available to the parent. Child reads require an assigned owner. |
| PlayerAchievement | Account ID, nullable child profile ID, achievement key, avatar ID, unlock time | Unique per assigned child and achievement. Unlocks are permanent and idempotent. |
| Championship | Account ID, nullable child profile ID, point table and status | Championship points use 10, 8, 6, 4, 2. Completion grants +500 XP once. |
| LegacyAssignment | Parent account, selected child, assignment time | Parent-only audit record. Assignment must be atomic for the selected data group. |
| OfflineResult | Child profile, result payload, idempotency key, sync state | Retained until the server confirms success. |
| GeneratedImageCheck | Image/job ID, check name, result, checked time | All required checks must pass before storage or publication. |

## State transitions

### Race

`created -> completed`

Only a completed race accepts a result. Repeated submission with the same key
returns the saved result. A failed transaction leaves the race available for a
safe retry.

### Legacy assignment

`unassigned -> assigned(child_profile_id)`

Only the parent account can assign records. Each record has at most one child
owner. A failed assignment changes no records.

### Generated image

`generated -> validating -> passed -> stored -> published`

Any failed or unavailable required check moves the job to a failed or retrying
state. The image remains private.

### Offline result

`queued -> syncing -> synced`

On a network error, return to `queued`. Do not change the idempotency key.
