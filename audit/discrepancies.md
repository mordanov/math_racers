# Requirements and implementation gaps

## Purpose

This audit compares the product and technical requirements with the code.
It uses the document order in `docs/README.md` and
`initial_spec/speckit_constitution.md`.

The audit covers the product requirements, gameplay, progression, avatar,
statistics, interface, AI, and engineering requirements. It does not audit
artwork or prompt text. It does not include a run-time performance or
penetration test.

## Terms

- **API:** a defined way for the frontend and backend to exchange data.
- **CSRF:** a request from another site that uses a player's active session.
- **Safe retry:** a repeated request does not create a second result or reward.
- **Transaction:** a set of database changes that all succeed or all fail.

## Confirmed gaps

| ID | Priority | Requirement | Current implementation | Effect |
|---|---|---|---|---|
| D-01 | Critical | The game mode specification defines one request to create a race session and a separate request to save its result. | The frontend sends both requests to `POST /api/v1/races`. The backend route accepts a completed `RaceSummaryRequest`. The session request does not contain the required fields. (`frontend/src/features/race/raceSessionApi.ts:18-30`; `backend/app/races/presentation/api/v1/races.py:20-28`; `backend/app/races/schemas.py:23-32`) | The normal race setup cannot create a session against this API. The race flow does not follow the published contract. |
| D-02 | Critical | Child profiles must own their data. A parent must be able to manage and delete each child's data. | The selected child ID stays in frontend authentication state. The shared API client does not send it. Avatars and child profiles use `account_id`. The avatar request has no `child_profile_id`. (`frontend/src/infrastructure/auth/AuthContext.tsx:42,98-107`; `frontend/src/infrastructure/api-client.ts:18-42`; `backend/app/avatars/models.py:38`; `backend/app/avatars/schemas.py:20-35`; `backend/app/child_profiles/models.py:18-23`) | Children in one account do not have separate avatars or statistics. Deleting a profile cannot delete data for that child. |
| D-03 | High | XP and statistics must be linked to the player who took part in the race. | The race engine sorts participants by distance. The backend selects first place for XP. The statistics service selects the first participant in the request. (`frontend/src/engine/race/raceEngine.ts:174-190`; `backend/app/races/domain_service.py:46-50`; `backend/app/statistics/domain_service.py:34-36`) | An AI winner can receive the player's XP and achievements. Statistics can use an AI avatar ID as a UUID and fail. |
| D-04 | High | Training has no opponents, no time pressure, no finish line, and no XP. It continues until the player exits. | The race engine creates eight problems for every mode. The client calculates Training XP. The backend awards race XP and answer XP for every saved result. (`frontend/src/engine/race/raceEngine.ts:20-22,61,132-134`; `backend/app/progression/domain_service.py:25-30`) | Training does not match its documented behaviour. It can award XP, and it is not open-ended. |
| D-05 | High | The achievement requirements list achievements for racing, maths, collection, exploration, streaks, improvement, and other play. Triggers must evaluate the relevant events. | The catalogue has eight entries. The evaluator handles four race keys and three level keys. The hidden `hidden_speedster` entry has no evaluator. (`backend/app/achievements/catalogue.py:1-96`; `backend/app/achievements/domain_service.py:83-84,153-163`) | Most documented achievements cannot unlock. The achievement screen cannot meet the stated feature scope. |
| D-06 | High | The parent summary must show the strongest and weakest operation. Player statistics must show the favourite operation. | The response schemas set these fields to `None`. Race summaries do not include counts by operation. (`backend/app/statistics/schemas.py:8-18,53-61`; `backend/app/races/schemas.py:13-32`) | The parent dashboard cannot show required operation results. |
| D-07 | High | Generated images must pass technical and child-safety checks before publication. | The image check tests dimensions, alpha mode, file size, and non-empty pixels. It does not check text, watermarks, cropped characters, or unsafe content. (`backend/app/avatars/generation_service.py:58-76,260-263,310-327`) | An image that fails the documented content rules can reach a child. |
| D-08 | High | State-changing API requests need CSRF protection. Authentication and generation endpoints need rate limits. | The inspected API middleware registers correlation-ID middleware. The authentication routes set a refresh cookie, but no CSRF check was found. Avatar generation has count limits. No login or registration rate limit was found. (`backend/app/main.py:122`; `backend/app/presentation/api/v1/auth.py:45-64`; `backend/app/avatars/domain_service.py:21-24,105-121`) | The implementation does not meet the documented API security controls. |
| D-09 | Medium | Offline use must keep cached avatars and statistics available. Training must work offline. | The interface detects `navigator.onLine` and disables other modes. It still requests the avatar list. If that request fails, it redirects to avatar creation. (`frontend/src/shared/hooks/useOffline.ts:1-14`; `frontend/src/pages/RaceSetupPage.tsx:48-63,136-158`) | A player without a successful avatar-list request cannot start Training offline. Cached statistics are not available in the inspected flow. |
| D-10 | Medium | Tier 6 uses custom settings that a parent can select. | The frontend race setup offers Tiers 1–5. The backend tier table has Tiers 1–5. The frontend generator uses Tier 5 settings when Tier 6 has no custom settings. (`frontend/src/pages/RaceSetupPage.tsx:231-253`; `frontend/src/engine/math/tiers.ts:3-21`; `frontend/src/engine/math/generator.ts:65`; `backend/app/mathematics/tiers.py:17-37`) | A parent cannot use the documented custom tier. A request for Tier 6 can use the wrong problem rules. |
| D-11 | Medium | Use an AI provider abstraction and an S3-compatible storage adapter. The image provider must use GPT Image. | The generation service creates OpenAI clients and an S3 client directly. It names `gpt-4o-mini` and `dall-e-3` in the service. (`backend/app/avatars/generation_service.py:92-110,125-159,306`) | A provider or storage change requires edits to the generation service. The image model does not match the stated GPT Image requirement. |
| D-12 | Medium | The documents disagree on when to award the +500 championship bonus. The XP specification also defines a daily-challenge award and endpoint. | The backend adds +500 XP to each championship race. No daily-challenge route or award flow is registered. (`backend/app/progression/domain_service.py:25-30`; `backend/app/main.py:146-157`) | The reward may be too high. The daily-challenge requirement has no implementation. |
| D-13 | Medium | Race results, XP, statistics, and achievements must update as one safe operation. Statistics must update in the same transaction as the race result. | Race persistence, XP, achievements, and statistics run in one domain service. Statistics errors are caught and logged. There is no safe-retry key in the request schema. (`backend/app/races/domain_service.py:32-84`; `backend/app/races/schemas.py:13-32`) | Race, reward, and statistics records can disagree. A repeated result does not return the original result as the specification requires. |
| D-14 | Medium | The backend uses thin API routes and communicates between domains through application services and events. | The race domain service directly creates progression and achievement services. Child-profile routes enforce profile limits and ownership. (`backend/app/races/domain_service.py:44-69`; `backend/app/child_profiles/presentation/api/v1/child_profiles.py:41-69`) | Domain rules and orchestration are coupled. It is harder to test and change one domain without another. |

## Requirement conflicts and open decisions

The documents give different rules for these items. The implementation cannot
be judged until the project selects one rule.

| ID | Conflict | Evidence and current code |
|---|---|---|
| R-01 | Championship points are `10, 7, 5, 3, 1` in the feature document and `10, 6, 3, 1, 0` in the implementation specification. The frontend uses `10, 6, 3, 1, 0`. | `docs/gameplay/feature-game-modes.md`; `docs/gameplay/spec-game-modes.md`; `frontend/src/engine/race/raceEngine.ts:18` |
| R-02 | Tier 3 and Tier 4 operation sets differ between the feature document and the PRD and implementation specification. The code follows the PRD and implementation specification. | `docs/gameplay/feature-math-engine.md`; `docs/prd.md`; `docs/gameplay/spec-math-engine.md`; `frontend/src/engine/math/tiers.ts` |
| R-03 | The feature document says Training awards no XP. The detailed mode specification says no race-completion XP, but still allows correct-answer XP. The PRD awards XP for correct answers and race completion. | `docs/gameplay/feature-game-modes.md`; `docs/gameplay/spec-game-modes.md`; `docs/prd.md` |
| R-04 | The mode feature says Training is solo practice without time pressure. The detailed mode specification says it has an infinite problem loop. The game engine gives all modes eight problems. | `docs/gameplay/feature-game-modes.md`; `docs/gameplay/spec-game-modes.md`; `frontend/src/engine/race/raceEngine.ts:61` |
| R-05 | One level table starts Level 1 at 0 XP. Another specification says Level 1 requires 100 XP. The formula returns level 0 at 0 XP. | `docs/economy/feature-xp-progression.md`; `docs/economy/spec-xp-progression.md`; `backend/app/progression/domain_service.py:17,91` |
| R-06 | The asset pipeline says content checks block publication. The avatar generation specification says content checks are not blocking in v1.0. The code does not run content checks. | `docs/ai/asset-pipeline.md`; `docs/content/spec-avatar-generation.md`; `backend/app/avatars/generation_service.py:58-76` |
| R-07 | The PRD lists daily-challenge XP, but the v1.0 game-mode list does not define a daily challenge. The detailed XP specification names an endpoint that is not implemented. | `docs/prd.md`; `docs/economy/spec-xp-progression.md`; `docs/gameplay/spec-game-modes.md` |
| R-08 | One XP document awards +500 XP when a championship is completed. Another awards +500 XP for each championship race. The backend awards the bonus on each race. | `docs/economy/feature-xp-progression.md`; `docs/economy/spec-xp-progression.md`; `backend/app/progression/domain_service.py:25-30` |

Resolve these rules before implementation. Use the source-document order in the
Constitution if the owners do not choose a rule.

## Requirements that need run-time evidence

Code inspection cannot prove these targets. The project must test them on the
target environment:

- Startup under 3 seconds.
- Race loading under 2 seconds.
- Problem generation under 1 millisecond.
- At least 30 frames per second on supported devices.
- Current stable Chrome, Edge, Firefox, and Safari.
- Daily backup and restore. The infrastructure specification marks this check
  as open.
- Keyboard use, screen-reader output, colour contrast, and reduced motion.

## Remediation status

The implementation branch contains remediation code and local test evidence.
See `specs/014-audit-remediation/quickstart.md` for the evidence and the checks
that remain. The full backend integration suite passed with 85 tests on an
isolated PostgreSQL 16 and Redis test stack. It includes a race where the AI
wins, child-scoped legacy assignment and export, operation statistics, and
achievement replay. No discrepancy is marked closed.

Migration round-trip and data restore checks passed on PostgreSQL 16. A
PostgreSQL 18.6 host client failed against that server, so the restore script
was run with matching PostgreSQL 16 tools. `make ci` stopped at the formatting
check because the backend runtime image does not include Black. The standalone
backend format, lint, type, unit, and integration checks passed. Frontend
format, lint, type, test, and production-build checks passed.
Configured provider checks, target performance, browser, and accessibility
checks are not complete.

## Evidence

- Product requirements: `docs/prd.md` sections 3 and 4.
- Race and mode requirements: `docs/gameplay/feature-game-modes.md` and
  `docs/gameplay/spec-game-modes.md`.
- Progression requirements: `docs/economy/feature-xp-progression.md` and
  `docs/economy/spec-xp-progression.md`.
- Backend and security requirements: `docs/engineering/technical-requirements.md`
  and `docs/engineering/spec-backend-foundation.md`.
- Avatar and asset requirements: `docs/content/spec-avatar-generation.md`,
  `docs/ai/ai-architecture.md`, and `docs/ai/asset-pipeline.md`.
- Code references appear in each gap above. They identify the inspected
  implementation surface. They are not a claim that every related file was
  tested at run time.
