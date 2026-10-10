# Refactoring recommendations

## Purpose

These changes address the gaps in `discrepancies.md`. They also reduce coupling.
The first four items are needed for the planned repair. The other items improve
the system, but they are not a reason to delay the main game flow.

## Priority

| Order | Recommendation | Change | Reason |
|---|---|---|---|
| 1 | Define one race API contract | Separate session creation from result submission. Share request and response schemas between the backend and frontend. Add contract tests for both requests. | The current client request does not match the backend route. |
| 2 | Make child profile the data owner | Add `child_profile_id` to child-owned data. Apply one ownership check to every child API. Pass the selected child ID with every request. Add a migration and a documented rule for existing account data. | Account-level ownership combines sibling data and blocks per-child deletion. |
| 3 | Identify the human participant in a race | Send an explicit player or child ID in the race result. Do not infer the player from the finishing position or list order. Validate that the player owns the selected avatar. | The first participant can be an AI runner. |
| 4 | Add one race-result use case | Move result persistence, XP, statistics, and achievements into one application use case. Use one transaction. Make retries return the saved result. | This keeps related records consistent and removes cross-domain work from `RaceDomainService`. |
| 5 | Define Training as a separate mode | Give Training an open problem loop and a clear exit action. Disable race timing and opponents. Apply the approved XP rule in both the frontend and backend. | The current shared eight-checkpoint flow cannot meet the Training requirements. |
| 6 | Store operation-level answer data | Include the operation and answer outcome in the result. Use it to calculate strongest, weakest, and favourite operations. | The statistics service cannot derive these values from totals. |
| 7 | Use explicit achievement events | Define event types for races, answers, avatars, levels, and streaks. Map each achievement to an event and a tested rule. Keep unlock persistence idempotent. | The current evaluator only handles race and level rules. |
| 8 | Add AI and storage adapters | Define provider and object-storage interfaces. Move OpenAI and S3 calls into infrastructure adapters. Keep the generation workflow in the application layer. | This follows the provider-neutral design and makes external services easier to replace and test. |
| 9 | Make image safety checks an explicit gate | Define the blocking checks. Run the checks before publication. Keep the generated image private until all required checks pass. | Technical image checks alone do not establish child-safe content. |
| 10 | Add an offline data store | Cache the selected child's avatars and statistics. Let Training use local data. Record results locally and sync them when the network returns. | `navigator.onLine` alone does not provide offline access. |
| 11 | Apply API controls in shared middleware | Add CSRF protection and rate limits for login, registration, and generation. Test the controls at the API boundary. | Security rules should not depend on each route author. |
| 12 | Keep route handlers thin | Move profile limits and ownership rules from route handlers to application or domain services. Keep HTTP parsing and response mapping in the presentation layer. | This follows the backend module pattern. |

## Suggested boundaries

Use the existing modular structure. Do not add a general event platform for one
feature. Add only the interfaces that the race result and avatar flows need.

Use repository methods for persistence. Do not add new SQL queries to route
handlers. Keep provider credentials and provider-specific request models inside
infrastructure.

Keep the user's accepted product rules in the requirements documents. Update
the feature documents and implementation specifications at the same time as
the code.

## Completion checks

- A contract test covers race creation and result submission.
- A race result uses the explicit human participant.
- A retry does not create a second result, XP event, statistic update, or unlock.
- A child cannot read or change another child's data.
- Training follows the selected duration and reward rules.
- Tests cover each available achievement event.
- Offline Training works without an avatar-list network request.
- AI and storage calls are replaceable through their interfaces.
