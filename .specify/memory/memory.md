# Math Racers — Agent Memory

_Last updated: 2026-08-12_

---

## Completed Features

### spec 008 — XP & Player Progression (branch `main`, fully merged)

All 18 tasks complete (`specs/008-xp-progression/tasks.md`).

**What was built:**
- Alembic migration `0008_add_progression.py`: adds `longest_streak` column to `race_participants`, creates `player_progressions` and `xp_events` tables with indexes.
- `app/progression/` module: `models.py`, `schemas.py`, `repository.py`, `domain_service.py`, `presentation/api/v1/progression.py`.
- `GET /api/v1/progression` endpoint — returns `ProgressionResponse` for authenticated users.
- `POST /api/v1/races` now awards XP and returns `progression` in the response body.
- XP formula: `100 (race) + problems_correct×20 + floor(longest_streak/5)×10 + 500 if championship`.
- Level formula: `floor(sqrt(total_xp / 100))`; `xp_to_next_level` never < 1.
- Unit tests: 137 pass (`pytest -m unit`). Integration tests: 61 pass (`pytest -m integration`), including 6 progression-specific tests.

**Schema change:** `ParticipantSummaryRequest` now has a required field `longest_streak: Annotated[int, Field(ge=0)]`. Any new test constructing this schema must include it.

---

## Infrastructure Fix — CI Script Port Collision

`scripts/run-local-ci-checks.sh` was updated to handle port conflicts from other running Docker projects (e.g. a `chatbot` project holding ports 5432 and 6379).

**Change:** Added dynamic-port fallback for Postgres (`PG_PORT`, default 5432) and Redis (`REDIS_PORT`, default 6379) using the same `port_is_listening` / `find_free_port` Python helpers already used for the backend HTTP port. The `DATABASE_URL` and `REDIS_URL` env vars in the integration test section are parameterised on these variables.

**Status:** Modified but not yet committed — the CI "Verify clean working tree" check will fail until these changes are committed alongside the progression feature files.

---

## Pending Action

Commit all outstanding changes (progression feature + CI script fix) so the full `scripts/run-local-ci-checks.sh` run passes end-to-end including the "Verify clean working tree" → Docker image build → Trivy/pip-audit security scan stages.

---

## Project Conventions (observed)

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, pytest with `@pytest.mark.unit` / `@pytest.mark.integration` markers, ruff + black + mypy.
- Frontend: TypeScript, React, Vite, pnpm, eslint + prettier + vitest.
- Module pattern: each domain in `app/<domain>/` with `models.py`, `schemas.py`, `repository.py`, `domain_service.py`, `presentation/api/v1/<domain>.py`; router registered in `app/main.py`.
- Integration tests use a `_register_and_approve()` helper (see `tests/integration/championships/test_api_championships.py`) and run against a live stack (uvicorn + Postgres + Redis spun up by the CI script).
- CI script lives at `scripts/run-local-ci-checks.sh`; run from repo root; set `ALLOW_DIRTY_TREE=1` to skip the clean-tree gate during local troubleshooting.
