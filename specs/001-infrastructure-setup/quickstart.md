# Quickstart: Infrastructure Setup

**Audience**: Developers and operators setting up Math Racers locally or
deploying to a new environment.

---

## Prerequisites

- Docker and Docker Compose v2 installed (`docker compose version`)
- Git
- `make` (optional but recommended)
- For production: a domain name with DNS pointed at the server, and a
  Let's Encrypt-compatible ACME client available

---

## Local Development Setup

### 1. Clone and configure secrets

```bash
git clone <repo-url> math-racers
cd math-racers
cp .env.example .env
# Edit .env — fill in all required values (see .env.example for descriptions)
```

### 2. Start all services

```bash
docker compose up
# Or: make up
```

All five services start in dependency order:
`postgres` and `redis` → `backend` and `worker` → `nginx`.

Database migrations run automatically before the backend accepts traffic.

### 3. Verify the stack is healthy

```bash
curl http://localhost/health
# Expected: {"status":"ok","version":"...","checks":{"database":"ok","redis":"ok","storage":"ok"}}
```

### 4. Confirm migrations applied

```bash
docker compose exec backend alembic current
# Should match: alembic heads
```

---

## Running the CI Pipeline Locally

```bash
make ci
# Equivalent to: all 8 CI steps run in sequence
```

Individual steps:

```bash
make fmt-check     # Black + Prettier
make lint          # Ruff + ESLint
make type-check    # mypy --strict + tsc --noEmit
make test-unit     # pytest -m unit + vitest run
make test-int      # pytest -m integration (requires Docker)
make build         # docker build (both images)
make security-scan # trivy + pip-audit + npm audit
```

---

## Running a Database Migration

Create a new migration after changing a SQLAlchemy model:

```bash
docker compose exec backend alembic revision --autogenerate -m "add_user_preferences"
# Review the generated file in backend/alembic/versions/
docker compose restart backend   # Migration applies automatically on restart
```

Roll back one migration:

```bash
docker compose exec backend alembic downgrade -1
```

---

## Secrets Reference

See `.env.example` for all required environment variables. Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL DSN — e.g., `postgresql+asyncpg://user:pass@postgres:5432/mathracers` |
| `REDIS_URL` | Redis URL — e.g., `redis://redis:6379/0` |
| `JWT_SECRET` | Random 32-byte hex string (rotate to invalidate all sessions) |
| `OPENAI_API_KEY` | OpenAI API key (can be invalid locally to test graceful degradation) |
| `STORAGE_ENDPOINT` | S3-compatible endpoint |
| `STORAGE_ACCESS_KEY` | Storage credentials |
| `STORAGE_SECRET_KEY` | Storage credentials |
| `STORAGE_BUCKET` | Bucket name for generated assets |

---

## Simulating Failure Scenarios

**Redis down** (tests graceful degradation):
```bash
docker compose stop redis
curl http://localhost/health
# Expected: status "degraded" with redis "unavailable"
```

**Storage unreachable** (set invalid STORAGE_ENDPOINT in .env):
```bash
# Edit .env: STORAGE_ENDPOINT=http://invalid-host
docker compose restart backend
curl http://localhost/health
# Expected: status "degraded", storage "unavailable"
# Avatar generation requests return HTTP 503 with STORAGE_UNAVAILABLE code
```

**Invalid OPENAI_API_KEY**:
```bash
# Edit .env: OPENAI_API_KEY=invalid
docker compose restart backend
curl http://localhost/health
# Expected: status "ok" (invalid key does not block startup)
# AI generation attempts return a user-friendly error, not a stack trace
```

---

## Production Deployment

1. Ensure all CI steps pass on the default branch.
2. CI builds and tags the image with the git SHA.
3. Deploy: `VERSION=<git-sha> docker compose -f docker-compose.yml up -d`
4. Migrations run automatically before traffic is accepted.
5. Monitor `/health` until all checks return `ok`.

**TLS**: Point your domain at the server, ensure port 80 and 443 are open,
and start the ACME certificate agent before starting Nginx in production mode.

---

## Backup and Restore

**Trigger a manual backup**:
```bash
bash scripts/backup/pg-backup.sh
```

**Verify backup integrity**:
```bash
# Restore to a temporary database and confirm data
bash scripts/backup/pg-restore.sh <backup-file> mathracers_verify
```

Run a full restore test at least monthly. Document the result.
