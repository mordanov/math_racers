# Quickstart: Audit Remediation

## Setup

1. Use the project-supported environment and start the Docker Compose stack.
2. Apply Alembic migrations to a disposable database.
3. Run backend unit tests and frontend Vitest tests before implementation.
4. Create a parent with two child profiles and seed legacy account-owned data.

## Acceptance walkthrough

1. Select one child and create an avatar. Confirm its owner is that child.
2. Create a race session, complete a race, and submit the result.
3. Submit the same result again. Confirm one race, one XP award, one statistics
   update, and one set of achievement unlocks.
4. Make an AI finish first. Confirm the human child receives the result and XP.
5. Try to access another child's avatar, race, progression, statistics, and
   achievements. Confirm each request is denied.
6. Try to access an unassigned legacy row as a child. Confirm it is not
   returned. Assign it as the parent, then confirm only the selected child can
   access it.
7. Run Training for at least nine answers. Confirm unlimited play, no timer or
   opponents, +20 XP per correct answer, and no race-completion award.
8. Complete a championship. Confirm points are 10, 8, 6, 4, 2 and +500 XP is
   awarded once at completion.
9. Trigger and retry a released achievement event. Confirm one unlock.
10. Cause a required image check to fail or time out. Confirm the image stays
    private and the child receives a safe message.
11. Attempt state changes without a valid CSRF token and exceed authentication
    rate limits. Confirm structured errors and no state change.
12. Cache child data, disconnect the network, finish Training, reconnect, and
    confirm one sync.
13. Run the repository's formatting, lint, type-check, unit, integration, and
    build commands. Test backup restore and record performance results.

## Database safety

Run the migration and downgrade against a database copy that contains multiple
accounts, multiple child profiles, and legacy rows. Confirm no row is lost.
Confirm legacy rows remain inaccessible to children until the parent assigns
them.

## Local validation evidence

Run on the implementation branch. Latest local results:

- `cd backend && pytest -q -m unit` — 122 passed; 225 were deselected.
- `cd backend && ruff check . && mypy . && black --check .` — passed.
  Mypy checked 204 files. Black checked 219 files.
- `cd frontend && pnpm vitest run` — 377 passed in 53 files.
- `cd frontend && pnpm tsc --noEmit` — passed.
- `cd frontend && pnpm eslint src` — passed.
- `cd frontend && pnpm prettier --check "src/**/*.{ts,tsx,css,json}" --ignore-unknown` — passed.
- `git diff --check` — passed.
- The CSRF bootstrap API test passed against the local Compose backend. It
  returned 204 and set the CSRF cookie.
- On PostgreSQL 16, migration downgrade from head to 0012 and upgrade to head
  preserved account, child, avatar, race, race-session, and participant counts.
  Legacy avatars and races remained unassigned after the round trip.
- A PostgreSQL 16 dump restored into a second database with the repository
  restore script and matching PostgreSQL 16 tools. The script verified the
  checksum. Counts for accounts, children, races, answers, and child
  progression matched. A host PostgreSQL 18.6 client failed against the
  PostgreSQL 16 server because it sent the unsupported `transaction_timeout`
  command; use matching PostgreSQL 16 restore tools for this target.
- Focused race and progression backend tests — 54 passed. They include atomic
  XP increments, zero-XP Training, per-question Training seed validation, and
  server-derived race and AI results.
- Focused race setup, race engine, API, and offline store frontend tests — 20
  passed. They check the result payload and the cached offline tier.
- `pytest -q -m integration tests/integration` — 85 passed against isolated
  PostgreSQL 16 and Redis test services. This includes an AI-first result where
  the human receives XP, statistics from saved answer operations, child-scoped
  race flows, and parent-authorized legacy progression assignment, export, and
  child deletion.
- Child deletion and offline-store tests passed. They confirm that deletion
  removes only that child's cache and queued results. The tests also confirmed
  that another child's championship is hidden with a 404 response.
- Earlier focused child-data, achievement, race-result, Tier 6, Training, and
  parent dashboard tests passed. These include a check that parent assignment
  can include legacy avatar statistics and that the hidden speedster achievement
  needs a fast non-Training win.

## Audit item status

These are code and local test results. They are not final acceptance. Keep every
audit item open until the checks in the last column pass.

| Item | Local implementation evidence | Acceptance still needed |
|---|---|---|
| D-01 | Separate session and result contracts; session, answer, and retry API flows passed in the 81-test integration suite. | Review the complete frontend-to-API race flow in a supported browser. |
| D-02 | PostgreSQL 16 migration round trip; API test confirms unassigned legacy progression is hidden from export, parent assignment works, two children export separate XP, and deleting one child preserves the other. | Complete API checks for all child-owned data types, cross-child reads and writes, and full deletion/export contents. |
| D-03 | Server derives the human's result and AI standings. The full integration suite passed, including the AI-first API flow where the human receives XP. | Keep open until the full acceptance review confirms all race result requirements. |
| D-04 | Open Training, answer XP, and zero-answer exit logic have unit tests. | Test Training exit, rewards, and offline use in the browser. |
| D-05 | Achievement unit tests cover race, speed, and level predicates. API tests cover first-race and perfect-race unlocks, child-scoped reads, and idempotent replay without duplicate unlocks. | Test every released trigger and duplicate event through the API. |
| D-06 | Statistics API test derives favourite, strongest, and weakest operations from saved multiplication and division answers. The backend integration suite passed all 85 tests. | Verify the dashboard displays the API summary in a supported browser. |
| D-07 | Blocking image checks have generation unit tests. | Test unsafe and unavailable checks with the provider and storage service. |
| D-08 | CSRF, auth limits, and concurrent avatar-generation limits passed unit and API-boundary integration tests. | Test all mutation methods and generation limits in the target deployment. |
| D-09 | Offline storage, cached tier, setup, and child-data deletion have frontend tests. | Test offline Training and retry sync in a supported browser. |
| D-10 | Tier 6 saved settings passed through the API integration flow. | Test parent settings and generated problems in a supported browser. |
| D-11 | AI and storage adapters have unit tests. | Test the configured provider and object store in the target environment. |
| D-12 | One-time championship XP has progression tests; championship completion passed through the API; daily challenge is excluded from v1.0. | Verify exactly one completion award across retries and rollback failures. |
| D-13 | Idempotent result retries passed through the API integration suite; transaction use cases have unit tests. | Test rollback and consistent statistics after injected failures. |
| D-14 | Profile limits and ownership checks now run in an application use case. The child-profile API tests passed after the route refactor. | Complete the full architecture review and API tests across all domains. |

## Blocked acceptance checks

`docker-compose` 2.37.1 works. The backend and worker images built, and the
Compose health check passed when `HEALTH_URL=http://localhost:8000/health` was
set. The default health check uses port 80, but this Compose file exposes the
backend on port 8000.

`make ci` stopped at `fmt-check`. The backend runtime image does not include
Black, so the container could not run the formatting check. The isolated
backend and frontend format, lint, type, and unit checks passed outside that
runtime image. The build target also requires a clean worktree, so it cannot
run on this implementation branch without a commit.

An earlier backend integration run used the regular Compose database and shared
Redis rate limits. That run was invalid and ended with 43 failed, 27 passed,
and 8 errors. The later full run used an isolated PostgreSQL 16 database and
Redis instance and passed all 85 integration tests. No Docker volumes were
deleted.

The graph update was not run. The incremental scan found changed source files
and seven changed documents. The repository instruction requires an AST-only
update without semantic extraction costs, so the document changes were not
sent for semantic extraction.

The API race flows and rate-limit checks passed in the isolated integration
suite. Full child-data assignment, export, and deletion checks, configured
provider and storage checks, performance targets, browser IndexedDB,
accessibility, and supported-browser checks remain unverified. Run the restore script with a PostgreSQL 16-compatible client when the target
server is PostgreSQL 16. Do not close any audit finding until these checks and
the remaining implementation work have evidence.
