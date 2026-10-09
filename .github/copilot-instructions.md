# Copilot Instructions — Math Racers

Math Racers is a math-practice racing game for kids with a FastAPI backend and a
React/TypeScript frontend, deployed via Docker Compose behind nginx.

## Architecture

- **Backend (`backend/app/`)**: a modular monolith. Each domain (`accounts`,
  `achievements`, `avatars`, `championships`, `child_profiles`, `mathematics`,
  `opponents`, `progression`, `races`, `statistics`) is a self-contained module
  with its own `models.py`, `repository.py`, `domain_service.py`, `schemas.py`,
  and `presentation/api/v1/` (FastAPI routers). Top-level routers are wired in
  `backend/app/presentation/api/v1/` and mounted in `backend/app/main.py`.
  Cross-cutting middleware (auth, correlation ID, child-profile context) lives
  in `backend/app/presentation/api/middleware/`.
- **`backend/application/`** holds use-case scripts for account lifecycle
  (register/approve/reject/login/logout/refresh) that sit above the
  `accounts` domain module.
- **`backend/infrastructure/`**: DB engine/session setup (SQLAlchemy async),
  config (pydantic-settings), logging, and a Redis-backed job queue with
  recovery logic (`infrastructure/queue/recovery.py`).
- **Migrations**: Alembic, one file per feature under
  `backend/alembic/versions/`, numbered sequentially (`0001_...` → `0012_...`).
  Add new migrations for schema changes to any domain module.
- **Frontend (`frontend/src/`)**: feature-sliced.
  - `engine/<feature>/`: API clients and domain types/logic (e.g.
    `engine/achievements/achievementsApi.ts`).
  - `features/<feature>/`: feature-specific UI logic (e.g. badge rendering).
  - `pages/`: route-level components, each with a co-located `*.test.tsx`.
  - `shared/`: design tokens, shared hooks/components, global animations.
  - `infrastructure/`: API client base (`api-client.ts`) and auth.
  - Routing is centralized in `src/router.tsx`.
- **Spec Kit workflow**: features are planned under `specs/<NNN-feature>/`
  (spec.md, plan.md, tasks.md) using the `speckit-*` skills/commands before
  implementation. `docs/` contains the longer-lived vision/PRD/feature/spec
  hierarchy (see `docs/README.md` for the full map); check the relevant
  `docs/**/spec-*.md` before implementing a feature already documented there.

## Build, lint, test

Run everything through `make` (wraps Docker Compose + pnpm); see `make help`
for the full list. Key targets:

```bash
make up              # start all services, then verify health
make down             # stop all services
make ci               # full local CI: fmt-check, lint, type-check, test-unit, test-int, build, security-scan
make fmt-check        # Black (backend) + Prettier (frontend)
make lint             # Ruff (backend) + ESLint (frontend)
make type-check       # mypy --strict (backend) + tsc --noEmit (frontend)
make test-unit        # pytest -m unit + vitest run
make test-int         # pytest -m integration (requires Docker stack)
make migrate          # alembic upgrade head (inside backend container)
```

Backend tests are marked `unit` or `integration` (see `backend/pyproject.toml`);
integration tests require the Docker Compose stack. To run a single backend
test:

```bash
docker compose run --rm backend pytest tests/unit/achievements/test_domain_service.py::test_name -m unit
```

For the frontend, run a single test file/case directly with vitest:

```bash
cd frontend && pnpm vitest run src/pages/HomePageAudio.test.tsx -t "test name"
```

mypy runs in `strict` mode; Ruff selects `E, F, W, I, N, UP, B, A, C4, RUF`
(see `backend/pyproject.toml` for the ignore list and rationale comments).

## Conventions

- Backend domain modules follow repository → domain_service → presentation
  layering; don't bypass the repository/domain_service to query the DB
  directly from a router.
- Pydantic v2 (`pydantic[email]`) is used throughout for schemas/settings.
- `B008` (Depends() in defaults) and `A001`/`A004` (builtin shadowing, e.g.
  `PermissionError`) are intentionally allowed — don't "fix" these.
- Frontend pages/components pair each file with an adjacent `*.test.tsx`
  rather than a separate `__tests__` tree; integration-style engine/component
  tests live under `frontend/tests/`.
- Feature work happens on branches named after the `specs/<NNN-feature>` slug
  (e.g. `009-achievements`) and merges to `main` via PR.
