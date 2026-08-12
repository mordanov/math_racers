# Implementation Plan: XP & Player Progression

**Branch**: `008-xp-progression` | **Date**: 2026-08-11 | **Spec**: [spec.md](spec.md)

## Summary

Add XP earning and player level progression to Math Racers. When a player submits a race result via `POST /api/v1/races`, XP is calculated from race completion, correct answers, streak bonuses, and mode bonuses, then credited atomically. A new `GET /api/v1/progression` endpoint exposes the player's current level and XP totals. The race submission endpoint is idempotent: duplicate `race_id`s are already rejected by the existing conflict check, preventing double-awarding.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, PostgreSQL  
**Storage**: PostgreSQL — two new tables (`player_progressions`, `xp_events`), one new column (`race_participants.longest_streak`)  
**Testing**: pytest — unit tests for domain logic, integration tests against the running stack  
**Target Platform**: Linux server (Docker container)  
**Project Type**: Web service (modular monolith)  
**Performance Goals**: XP award within the same request-response cycle as race submission  
**Constraints**: All writes in a single DB transaction; XP events are append-only  
**Scale/Scope**: One progression record per account; unbounded XP event history

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| §IV Architecture (modular monolith, no circular deps) | ✅ PASS | New `app/progression/` module follows existing pattern |
| §VI Simplicity | ✅ PASS | No speculative abstractions; LevelUpEvent not persisted |
| §VII Code Quality | ✅ PASS | Unit-testable formula, deterministic |
| §VIII Consistency | ✅ PASS | Matches `accounts`/`races`/`championships` module layout |
| §IX Backend owns progression | ✅ PASS | Specified in constitution §IX |
| §XIV Database schemas evolve through migrations | ✅ PASS | Migration `0008_add_progression.py` |
| §XVIII Testing | ✅ PASS | Unit tests for formula + service; integration test for API |
| §XXII Versioning (DB migrations) | ✅ PASS | Sequential migration number `0008` |

**No violations.** No Complexity Tracking table required.

## Project Structure

### Documentation (this feature)

```text
specs/008-xp-progression/
├── plan.md              ← this file
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── race-submission.md
│   └── progression-read.md
├── checklists/
│   └── requirements.md
└── tasks.md             ← /speckit-tasks output (not yet created)
```

### Source Code

```text
backend/
├── alembic/versions/
│   └── 0008_add_progression.py          # NEW — add tables + column
│
├── app/
│   ├── progression/                     # NEW module
│   │   ├── __init__.py
│   │   ├── models.py                    # PlayerProgression, XPEvent SQLAlchemy models
│   │   ├── repository.py                # ProgressionRepository protocol + SQLAlchemy impl
│   │   ├── domain_service.py            # XP formula, level calc, award logic
│   │   ├── schemas.py                   # Pydantic: ProgressionResponse, LevelUpEvent
│   │   └── presentation/
│   │       └── api/v1/
│   │           └── progression.py       # GET /api/v1/progression router
│   │
│   ├── races/
│   │   ├── schemas.py                   # MODIFIED — add longest_streak to ParticipantSummaryRequest
│   │   │                                # MODIFIED — add progression to RaceSummaryResponse
│   │   ├── domain_service.py            # MODIFIED — call ProgressionDomainService.award_xp()
│   │   └── models.py                    # MODIFIED — add longest_streak to RaceParticipant
│   │
│   └── main.py                          # MODIFIED — register progression router
│
└── tests/
    ├── unit/
    │   └── progression/
    │       ├── __init__.py
    │       ├── test_domain_service.py   # Formula, level calc, level-up detection
    │       └── test_schemas.py          # xp_to_next_level never negative
    └── integration/
        └── progression/
            ├── __init__.py
            └── test_api_progression.py  # Earn XP, idempotency, level-up, read endpoint
```

## Key Design Decisions

1. **XP award is synchronous** — happens inside `RaceDomainService.persist_race()`, within the same DB session/transaction as the race insert. Returns `ProgressionResponse` as part of `RaceSummaryResponse`.

2. **Idempotency via race_id uniqueness** — existing `RACE_ALREADY_EXISTS` conflict check prevents double-insert. XP is awarded only when the race row is newly created.

3. **PlayerProgression uses upsert** — `INSERT ... ON CONFLICT (account_id) DO UPDATE`. No need to check existence first.

4. **XPEvent is a single consolidated row per race** — one row with source `race_completion` and the total delta, not individual rows per bonus type. Simpler and sufficient for the spec requirement that "total_xp is derivable from summing XPEvent.amount."

5. **`longest_streak` added to `ParticipantSummaryRequest`** — new required field. No backwards-compat shim needed (this is a new feature, not a migration of existing clients).

6. **LevelUpEvent not persisted** — returned in response only. Storing it is deferred to when the achievement system is built.

7. **`GET /api/v1/progression` returns zero-state** — if no `PlayerProgression` row exists, returns `{total_xp:0, current_level:0, xp_to_next_level:100}` without creating a row. Row is created on first XP award.
