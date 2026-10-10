# One-sprint implementation plan

## Goal

Restore a working race flow. Keep each child's data separate. Apply the approved
rules for Training, XP, statistics, and achievements.

## Planning assumptions

- Sprint length: 10 working days.
- Team: two backend engineers, one frontend engineer, and one test or architecture
  engineer.
- Product and architecture owners can make the decisions in this plan on Day 1.
- No new feature is added outside the requirements in `docs/`.

The estimate depends on the team and the data migration decision. If the team is
smaller, reduce the scope before the sprint starts. Do not remove the contract,
ownership, or result-attribution tests.

## Decisions required on Day 1

Record one approved rule for each conflict in `discrepancies.md`:

1. Championship points.
2. Tier 3 and Tier 4 operations.
3. Training XP.
4. Training duration and timer behaviour.
5. The Level 1 XP threshold.
6. Image safety checks that block publication.
7. Daily-challenge scope for v1.0.
8. How to assign existing account-owned records to child profiles.

Do not guess how to divide existing family data. The product owner must approve
the migration rule before the schema change.

## Work plan

| Days | Owner | Work | Exit condition |
|---|---|---|---|
| 1 | Product owner, architect, team | Approve the eight decisions. Write the race API contract. Agree on the existing-data migration rule. | Approved rules and contract are in the requirements documents. |
| 2–4 | Backend and frontend | Add separate race-session and race-result endpoints. Update the frontend client. Include the human participant ID and result idempotency key. | Contract tests pass. Race setup and result submission use the matching endpoints. |
| 2–5 | Backend | Add child-profile ownership to avatars, races, progression, statistics, and achievements. Add the migration and move existing data by the approved rule. Apply ownership checks to read, write, export, and delete actions. Move profile limits and ownership rules out of route handlers. | Tests prove that one child cannot access another child's records. Profile deletion removes that child's data. |
| 4–6 | Backend and frontend | Add the race-result application use case. Save race, XP, statistics, and achievements in one transaction. Select the player by ID, not by rank. | A player who loses to an AI still receives the correct XP and statistics. A repeat request returns the saved result. |
| 4–7 | Frontend and backend | Implement the approved Training loop and reward rule. Keep Training separate from the eight-checkpoint race. Add Tier 6 settings and the parent selection flow. | Training meets the approved no-pressure, duration, and XP rules. Tier 6 uses saved parent settings. |
| 5–7 | Backend and frontend | Add operation-level answer data. Calculate strongest, weakest, and favourite operations. Update the parent summary. Add the daily-challenge award flow if the Day 1 decision keeps it in v1.0. | Tests return correct operation results. The daily challenge works or the documents mark it out of scope. |
| 6–8 | Backend and frontend | Add the approved achievement events and predicates. Remove or implement catalogue entries that do not have a trigger. | Every released achievement has a tested trigger and a persistent unlock. |
| 7–8 | Backend | Add CSRF protection and rate limits for authentication and generation. Add blocking image-safety checks from the approved rule list. Add interfaces for AI and object storage. Move client creation to infrastructure. | API tests prove that the controls work. An image cannot publish after a failed required check. The generation flow uses the new interfaces. |
| 7–9 | Frontend | Cache the selected child's avatar list and statistics. Allow Training to open offline. Queue completed results for sync. | With the network disabled, a player with cached data can start and finish Training. |
| 9–10 | Whole team | Run targeted unit, integration, and frontend tests. Run the full CI target. Test a database backup and restore. Measure the required startup, race-load, and problem-generation targets on the test environment. Review migrations, error messages, API documentation, and all requirement documents. Fix release-blocking failures. | CI passes. The acceptance checklist below passes. The documentation matches the code. Required operational and performance checks have results. |

## Sprint acceptance checklist

- [ ] Race setup creates a valid session.
- [ ] Race result submission uses a separate endpoint.
- [ ] The backend identifies the human participant by ID.
- [ ] A repeated result does not add duplicate race, XP, statistics, or achievement
  records.
- [ ] Each child can only access their own data.
- [ ] Parent export and delete actions apply to the selected child.
- [ ] Training follows the Day 1 decision.
- [ ] The parent summary shows strongest and weakest operations.
- [ ] Tier 6 uses parent-defined settings.
- [ ] Daily-challenge XP works or the approved documents exclude it from v1.0.
- [ ] Every visible achievement has a tested unlock rule.
- [ ] Required image checks block publication.
- [ ] The generation flow uses AI and storage interfaces.
- [ ] Route handlers do not contain profile or race business rules.
- [ ] Offline Training works with cached child data.
- [ ] CSRF and authentication rate-limit tests pass.
- [ ] The team completes a database backup and restore test.
- [ ] The team records results for startup, race-load, and problem-generation targets.
- [ ] The approved requirement decisions are recorded in `docs/`.

## Risks

| Risk | Action |
|---|---|
| Existing records belong to an account, not a child. | Require an approved backfill rule before migration work. Keep a database backup and test the migration on a copy. |
| The current race API does not create a session. | Fix the contract before UI work. Test client and server together. |
| The selected child ID is not part of API requests. | Add it to the shared API client and validate it on the backend. Do not rely on frontend state for access control. |
| AI content checks need an external safety service. | Confirm the approved checks and service before coding. If the check is unavailable, do not publish the image. |
| One sprint may not have enough capacity. | Protect the race API, child data ownership, result attribution, and Training fixes first. Re-plan remaining work with the product owner rather than silently dropping a requirement. |

## Design limit

Do not add a general event platform. Use the race-result use case and clear
events for the current flows. Do not add unrelated interface work.
