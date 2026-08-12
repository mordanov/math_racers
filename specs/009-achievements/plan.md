# Implementation Plan: Player Achievements

**Branch**: `009-achievements` | **Date**: 2026-08-12 | **Spec**: [spec.md](spec.md)

## Summary

Add a permanent achievement system to Math Racers. The backend evaluates achievement predicates whenever qualifying domain events occur (race completed, level-up) and records unlock records idempotently. Two read endpoints expose the catalogue and per-player unlocks. The frontend displays a sequential celebration animation on the Results Screen and never during an active race.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2 async, Alembic, pytest (backend); React, Vite, vitest (frontend)
**Storage**: PostgreSQL — two new tables: `achievements` (catalogue), `player_achievements` (unlock records)
**Testing**: pytest with `@pytest.mark.unit` / `@pytest.mark.integration`; vitest for frontend
**Target Platform**: Linux server (backend API); browser (frontend)
**Project Type**: Web service (modular monolith)
**Performance Goals**: Catalogue and unlock list queries resolve within 1 second
**Constraints**: Achievement unlock is idempotent; no direct-grant API; hidden achievements never leak before unlock
**Scale/Scope**: One new backend module (`app/achievements/`); one new frontend service + UI component

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| IV Architecture — modular monolith, separated domain/infra | ✅ PASS | New `app/achievements/` module follows existing pattern |
| V Documentation First | ✅ PASS | `docs/economy/spec-achievements.md` already authoritative |
| VI Simplicity | ✅ PASS | Catalogue is static; evaluation is pure predicate functions |
| IX Backend Principles — business logic not in controllers | ✅ PASS | Evaluation logic lives in `domain_service.py` |
| XIV Data Ownership — schema via migrations | ✅ PASS | New Alembic migration 0009 |
| XV Security — auth + least privilege | ✅ PASS | Catalogue is public; unlock list uses `get_current_account` |
| XVIII Testing | ✅ PASS | Unit + integration tests planned per feature |
| XXII Versioning — APIs versioned | ✅ PASS | Routes under `/api/v1/` |

No violations. Gate passed.

## Project Structure

### Documentation (this feature)

```text
specs/009-achievements/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
└── tasks.md             ← /speckit-tasks output
```

### Source Code

```text
backend/
├── app/achievements/
│   ├── __init__.py
│   ├── catalogue.py          # Static achievement definitions (key, category, title, description, hidden, icon_path)
│   ├── models.py             # PlayerAchievement ORM model (unlock records)
│   ├── schemas.py            # AchievementResponse, PlayerAchievementResponse, UnlockListResponse
│   ├── repository.py         # AchievementRepository protocol + SQLAlchemy implementation
│   ├── domain_service.py     # AchievementDomainService: evaluate(), unlock(); predicate registry
│   └── presentation/
│       └── api/v1/
│           └── achievements.py   # GET /api/v1/achievements, GET /api/v1/players/{id}/achievements
├── alembic/versions/
│   └── 0009_achievements.py  # player_achievements table + index
└── tests/
    ├── unit/achievements/
    │   ├── __init__.py
    │   ├── test_domain_service.py   # predicate evaluation, idempotency, hidden filter
    │   └── test_catalogue.py        # catalogue integrity (no duplicate keys, required fields)
    └── integration/achievements/
        ├── __init__.py
        └── test_api_achievements.py # GET catalogue, GET player achievements, unlock via race POST

frontend/
└── src/
    ├── engine/achievements/
    │   ├── achievementsApi.ts      # fetchAchievements(), fetchPlayerAchievements()
    │   └── types.ts                # Achievement, PlayerAchievement interfaces
    └── components/achievements/
        ├── AchievementToast.tsx    # Celebration animation (badge scale-in, sparkle, sound)
        └── AchievementToast.test.tsx
```

**Structure Decision**: Follows the established `app/<domain>/` pattern (models, schemas, repository, domain_service, presentation/api/v1). The achievement catalogue is a static Python module — no DB table required for catalogue entries, only for unlock records.

## Complexity Tracking

No constitution violations — table not required.
