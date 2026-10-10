# Implementation Plan: Audit Remediation

**Branch**: `014-audit-remediation` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)
**Input**: [Feature specification](spec.md)

## Summary

Close the confirmed gaps in the architecture audit. First add a real race
session and result flow, explicit child ownership, and idempotent result
processing. Then implement the approved game rules, child-safe generation,
security controls, offline Training, and operation-level statistics. Keep the
modular monolith. Use the existing application, domain, repository, and
infrastructure layers.

## Technical Context

**Language/Version**: Python 3.13; TypeScript  
**Primary Dependencies**: FastAPI, SQLAlchemy async, Pydantic, Alembic, Redis,
React, Vite, Vitest  
**Storage**: PostgreSQL, Redis, S3-compatible object storage, browser IndexedDB  
**Testing**: pytest unit and integration tests; Vitest; `make ci`  
**Target Platform**: Docker Compose backend and supported desktop/tablet browsers  
**Project Type**: Web application and API; modular monolith  
**Performance Goals**: startup under 3 s; race loading under 2 s; problem
generation under 1 ms; minimum 30 FPS  
**Constraints**: No new general event platform. Do not publish an image if a
required check fails or is unavailable. Do not expose unassigned legacy data to
children. Preserve existing child data during schema migration.  
**Scale/Scope**: Existing account, child-profile, avatar, race, progression,
statistics, achievement, and infrastructure modules; one cross-domain race
result use case; one parent legacy-data assignment flow; offline Training.

No technical choice requires external research. The project already uses the
required database, queue, AI SDK, and storage SDK. The current request session
commits once after the route completes; application orchestration can use that
request transaction and must not allow repositories to commit independently.

## Approved Requirements

- Championship points: 10, 8, 6, 4, 2 for places one through five.
- Training: unlimited problems, no timer or opponents, +20 XP per correct
  answer, and no race-completion XP.
- Tier 3: multiplication. Tier 4: division. Tier 6: saved parent settings.
- Level 1 starts at 0 XP. Level 2 starts at 400 XP.
- Championship completion grants +500 XP once.
- Daily Challenge remains a future feature and is outside v1.0.
- Image checks are automatic and block publication. Parental approval is not
  required in v1.0.
- The parent must assign legacy data before a child can access it. No record is
  assigned or divided automatically.

The source GDD, Game Economy specification, and derived `docs/` files must be
updated before the affected code changes.

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| Architecture: modular monolith and clear boundaries | PASS | Add one result use case and small infrastructure adapters. Do not add a general event platform. |
| Documentation first | PASS | Update source and derived requirements before implementation. |
| Simplicity | PASS | Reuse SQLAlchemy, Redis, OpenAI, and existing client patterns. Add no dependency unless existing tools cannot meet a requirement. |
| Backend rules stay out of routes | PASS | Routes validate input and call application use cases. |
| Data ownership and migrations | PASS | Add reversible Alembic changes. Keep legacy child ownership null until the parent assigns it. |
| AI and image generation | PASS | Keep prompts in the Prompt Builder. Put provider and storage calls behind infrastructure interfaces. Fail closed on safety checks. |
| Security and privacy | PASS | Validate child ownership on the server. Add CSRF and shared rate controls. |
| Testing and accessibility | PASS | Add regression, transaction, ownership, offline, keyboard, screen-reader, contrast, and reduced-motion checks. |
| Performance and backup | PASS | Measure stated targets and test restore in the target environment. |

No Constitution violation is required.

## Design

### Race flow

- `POST /api/v1/races` creates and persists a race session. It binds the
  authenticated parent, selected child, avatar, mode, tier, seed, and
  championship.
- `POST /api/v1/races/{race_id}/results` saves one result. The server uses the
  session's human avatar and child identity, not participant order or rank.
- Store the idempotency key with the result. A repeated key returns the saved
  response. A different result for an already completed session returns a
  conflict.
- One application use case orchestrates persistence, XP, statistics, and
  achievements. The request transaction commits only after all operations
  succeed.

### Child ownership

- Keep `account_id` for parent authorisation and add `child_profile_id` to
  child-owned records.
- Resolve the active child from a shared request header and validate ownership
  on the server. Use explicit child IDs for parent administration.
- Keep existing rows unassigned after migration. A parent-only workflow lists
  unassigned data and lets the parent assign each record or related record
  group to one child. Child queries exclude unassigned data.
- Convert account-level aggregates to child-level records while preserving one
  unassigned legacy aggregate per account until parent assignment.
- Do not remove a child's data until the parent confirms deletion.

### Progression, statistics, and achievements

- Store answer operation and correctness in the race result.
- Calculate operation statistics from saved answers with deterministic tie
  handling.
- Enforce the level baseline: `max(1, floor(sqrt(total_xp / 100)))`.
- Award answer XP in Training, but do not award race-completion XP.
- Award the championship bonus once when the championship changes to completed.
- Evaluate released achievement rules from explicit events. Keep unlock writes
  idempotent and inside the result transaction.

### Security and generation

- Add synchroniser CSRF tokens for state-changing requests. Validate token and
  request origin in shared middleware.
- Use Redis-backed rate limits for authentication. Keep avatar generation
  limits at the documented 2 concurrent jobs and 10 jobs per hour per account.
- Define AI and object-storage interfaces in infrastructure. Use the GPT Image
  provider and the existing Prompt Builder.
- Add a blocking image-safety check for the content rules in the GDD and asset
  pipeline. Do not store or publish an image until every required check passes.
  A check error blocks publication.

### Offline Training

- Store selected-child avatars and statistics in IndexedDB.
- Use cached avatar data to open Training without an API request.
- Queue a completed result with its original idempotency key. Sync it when the
  network returns. Show an error if sync fails; do not discard the queued result.

## Project Structure

### Documentation

```text
specs/014-audit-remediation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── race-and-child-data.md
└── tasks.md
```

### Source Code

```text
backend/
├── app/
│   ├── races/                       # session/result entities and repositories
│   ├── child_profiles/              # ownership and parent assignment
│   ├── progression/ statistics/ achievements/
│   ├── avatars/ ai/ assets/
│   └── presentation/api/middleware/ # child context, CSRF, rate limits
├── application/                     # cross-domain use cases
├── infrastructure/                  # provider, storage, Redis interfaces
├── alembic/versions/                # reversible schema migration
└── tests/{unit,integration}/

frontend/src/
├── infrastructure/                  # active child, CSRF, offline store
├── features/race/                   # session and result clients
├── engine/race/                      # player and answer summaries
├── features/statistics/
└── pages/                            # setup, results, Training, parent assignment
```

**Structure Decision**: Use the existing backend domain modules and feature
folders. Put orchestration in the application layer. Keep race simulation in
the browser. Add no new top-level service.

## One-Sprint Sequence

The estimate assumes 10 working days and the four-person team in
`audit/implementation-plan.md`.

| Days | Work | Gate |
|---|---|---|
| 1 | Update approved requirements. Add contract and migration designs. | Product rules and acceptance tests are recorded. |
| 2–4 | Race session/result API, player identity, idempotency, transaction tests. | Race contract and integration tests pass. |
| 2–5 | Child ownership migration, server checks, parent assignment flow. | No cross-child access; unassigned data stays hidden from children. |
| 4–7 | Training, XP, Tier 6, operation statistics, achievement events, championship rules. | Domain and frontend tests pass. |
| 7–9 | CSRF, auth rate limits, image safety, AI/storage adapters, offline Training. | API boundary and offline tests pass; failed image checks block release. |
| 9–10 | Full CI, restore test, accessibility review, performance measurement, documentation review. | Acceptance checklist and Constitution DoD pass or blockers are reported. |

## Risks and Controls

| Risk | Control |
|---|---|
| Legacy records combine data from multiple children. | Keep them inaccessible to children until the parent assigns an owner. Never infer or split ownership. |
| Large schema change affects existing accounts. | Test upgrade and rollback on a database copy; preserve account IDs and rows. |
| External safety service is unavailable. | Fail closed. Do not publish the image. |
| Offline results cannot sync. | Keep the result and idempotency key in IndexedDB; show a retry state. |
| Scope exceeds one sprint. | Do not remove requirements silently. Report measured blockers and remaining tasks. |

## Complexity Tracking

| Addition | Reason | Simpler alternative rejected |
|---|---|---|
| Legacy assignment state and parent flow | Existing data has no child owner; automatic assignment would expose or misattribute child data. | Assigning everything to the first profile would guess ownership. |
| IndexedDB outbox | Offline Training must preserve results until sync. | In-memory state is lost when the page closes. |
| Small provider interfaces | Current generation code constructs OpenAI and S3 clients directly. | Keeping provider calls in the service blocks replacement and tests. |
