# Backend Foundation — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** ADR-001; ADR-002; ADR-005; speckit_specification.md §22–43; technical-requirements.md
**Parent:** [Epic E6 — Engineering](../prd.md)
**See also:** [technical-requirements.md](technical-requirements.md), [spec-infrastructure.md](spec-infrastructure.md)

---

## Module Directory Layout

```
backend/
  app/
    accounts/           # auth, user registration, child profiles
    avatars/            # avatar CRUD, favourite management, metadata
    races/              # race sessions, results, championship state
    mathematics/        # difficulty settings, tier configuration
    statistics/         # race history, aggregated stats, weekly summary
    progression/        # XP events, level computation, level-up events
    achievements/       # catalogue, unlock records, evaluation
    assets/             # generated asset metadata, version tracking
    ai/                 # AI orchestrator, job queue, provider adapters
    shared/             # Result types, UUIDs, time abstraction, base exceptions
  infrastructure/
    database/           # SQLAlchemy engine, session factory, base model
    storage/            # object storage adapter interface + S3 implementation
    queue/              # Redis job queue adapter
    ai_providers/       # OpenAI adapter (implements AIProvider interface)
    config.py           # Pydantic BaseSettings
    logging.py          # structured JSON logging setup
  presentation/
    api/
      v1/               # FastAPI routers per domain (accounts, avatars, races, …)
      middleware/       # auth, correlation ID, CSRF, rate limiting
      error_handlers.py
  application/
    # application services (use case orchestrators) per domain
    create_avatar.py
    submit_race_result.py
    award_xp.py
    …
```

Each domain module is self-contained. No domain module imports from another domain module directly. Cross-domain communication happens through domain events and application service orchestration.

---

## Domain Module Interface Pattern

Every domain module exposes exactly four public surfaces:

| Surface | Responsibility |
|---------|---------------|
| Repository interface | Persistence abstraction (domain layer) |
| Domain service | Business rules and invariants |
| Application service | Use-case orchestration (calls repository + domain service + emits events) |
| REST router | HTTP boundary (calls application service; contains no business logic) |

Example — Avatar module:

```python
# avatars/repository.py
class AvatarRepository(Protocol):
    def get(self, avatar_id: UUID) -> Avatar | None: ...
    def save(self, avatar: Avatar) -> None: ...
    def list_for_player(self, player_id: UUID) -> list[Avatar]: ...

# avatars/domain_service.py
class AvatarDomainService:
    def validate_creation_input(self, input: AvatarCreationInput) -> None: ...
    def set_favourite(self, avatars: list[Avatar], target_id: UUID) -> list[Avatar]: ...

# application/create_avatar.py
class CreateAvatarUseCase:
    def execute(self, input: AvatarCreationInput) -> AvatarCreationResult: ...

# presentation/api/v1/avatars.py
router = APIRouter(prefix="/avatars")
@router.post("/")
async def create_avatar(input: AvatarCreationInput, ...): ...
```

---

## Authentication Flow

```
1.  POST /api/v1/auth/register  → validate email + password → hash password (bcrypt)
                                → INSERT account
                                → issue access_token (JWT, 15 min TTL)
                                        + refresh_token (opaque UUID, 30 days TTL)
                                → set refresh_token in HttpOnly cookie

2.  POST /api/v1/auth/login     → verify credentials → issue tokens (same as above)

3.  GET  /api/v1/...            → extract Bearer token from Authorization header
                                → validate JWT signature + expiry
                                → inject account into request scope

4.  POST /api/v1/auth/refresh   → read refresh_token cookie
                                → verify token exists + not revoked in DB
                                → rotate: issue new access_token + new refresh_token
                                → revoke old refresh_token

5.  POST /api/v1/auth/logout    → revoke refresh_token
                                → clear cookie
```

Child profiles do not have separate credentials. They are accessed under the parent's session with a child profile selector. API endpoints that act on a child profile validate that the `child_profile_id` belongs to the authenticated parent.

---

## Configuration

All configuration from environment variables via Pydantic `BaseSettings`. No hardcoded defaults for secrets.

```python
class Settings(BaseSettings):
    database_url: str               # no default
    redis_url: str                  # no default
    openai_api_key: str             # no default
    jwt_secret_key: str             # no default
    object_storage_bucket: str      # no default
    object_storage_endpoint: str    # no default
    object_storage_access_key: str  # no default
    object_storage_secret_key: str  # no default

    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30
    max_avatars_per_player: int = 50
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

`Settings` is instantiated once at startup and injected as a dependency. No module reads `os.environ` directly.

---

## Error Handling Hierarchy

```
Domain Layer:
  DomainError (base)
    ├── ValidationError       # invariant violation
    ├── NotFoundError         # entity does not exist
    ├── ConflictError         # duplicate, already exists
    └── PermissionError       # auth/authz failure

Application Layer:
  ApplicationError (wraps DomainError with context)

Presentation Layer:
  error_handlers.py maps ApplicationError subtypes → HTTP status + structured body:
    {
      "error_code": "AVATAR_NOT_FOUND",
      "message": "Avatar not found.",
      "request_id": "uuid"
    }
```

Domain never imports from `fastapi` or knows HTTP status codes. `ApplicationError` carries a `code` string that is mapped in the error handler.

---

## Health Endpoint

`GET /health` — publicly accessible, no authentication.

```json
{
  "status": "ok | degraded | down",
  "version": "1.0.3",
  "components": {
    "database": "ok | down",
    "worker_queue": "ok | down"
  },
  "request_id": "uuid"
}
```

`status == "degraded"` if any component is `down` but the API itself is serving. Returns HTTP 200 for `ok` and `degraded`; HTTP 503 for `down`.

---

## API Versioning

- All routes: `/api/v1/`
- Breaking changes require a new prefix `/api/v2/`; v1 is never modified for breaking changes
- Non-breaking additions (new optional fields, new endpoints) are made to v1

---

## Background Job Lifecycle

```
Pending → Running → Succeeded
                 → Failed → Retrying (attempt 1)
                            → Retrying (attempt 2)
                            → Retrying (attempt 3)
                                      → PermanentFailure
```

- Max 3 retries with exponential backoff: 30 s, 120 s, 480 s.
- Workers are stateless; any worker can pick up any job.
- Jobs are idempotent: re-running a succeeded job produces no side effects.
- Job state is stored in Redis (hot) and PostgreSQL (durable audit log).

---

## Correlation IDs

Every incoming request receives a `X-Request-ID` header (generated by middleware if absent). This ID propagates to:
- All log entries from that request
- Background jobs spawned from the request
- Error responses (`request_id` field)
- HTTP response header (`X-Request-ID`)

---

## Edge Cases

1. **Database connection lost at startup** — FastAPI lifespan raises immediately; the container exits with code 1; Docker Compose restarts it. Do not silently serve requests with no DB connection.
2. **Worker queue full** — Redis `LPUSH` returns the queue length. If queue length exceeds a configurable threshold (default 1000), the API returns HTTP 503 with `QUEUE_FULL` code.
3. **Migration fails mid-deploy** — Alembic's transaction-per-migration means a failed migration leaves the schema at the last successful version. The app refuses to start if `alembic current` does not match `alembic head`. The previous container continues serving until the new one passes health checks.
4. **Circular import between domain modules** — prevented architecturally: domain modules never import from each other. If a circular import occurs, it is a design violation (resolve via event or shared interface).
5. **JWT secret rotation** — old tokens become invalid immediately. Clients will receive HTTP 401 and must re-authenticate. This is acceptable and should be documented in the ops runbook.

---

## Manual Verification Steps

1. Start the stack with `docker compose up`. Call `GET /health`. Confirm `status == "ok"` and both `database` and `worker_queue` are `ok`.
2. Register a new parent account. Log in. Confirm `access_token` and `refresh_token` are returned. Confirm `refresh_token` is in an HttpOnly cookie.
3. Call a protected endpoint with the access token. Confirm HTTP 200. Wait for the token to expire (or set TTL to 1 min). Call again. Confirm HTTP 401.
4. Use the refresh endpoint to get a new access token. Confirm it works. Use the old refresh token again. Confirm it is rejected (rotated).
5. Start an avatar generation job. Kill the worker. Confirm the job retries. Restart the worker. Confirm the job eventually succeeds.
6. Submit invalid input to any endpoint (e.g., missing required field). Confirm HTTP 422 with an `error_code` and human-readable `message`. Confirm no stack trace appears in the response.
7. Disconnect the database container. Call `GET /health`. Confirm `status == "degraded"` and `database == "down"`.
8. Call `POST /api/v1/races/{id}/results` twice with the same `idempotency_key`. Confirm XP is awarded only once.

---

## Acceptance Criteria

- [ ] All domain modules are self-contained with no direct cross-domain imports.
- [ ] No business logic exists in FastAPI route handlers.
- [ ] All configuration is loaded from environment variables; no hardcoded secrets.
- [ ] Error responses use `error_code` + `message`; no stack traces in production.
- [ ] JWT access tokens expire in 15 minutes; refresh tokens rotate on use.
- [ ] Health endpoint reflects real database and worker queue status.
- [ ] Background jobs retry up to 3 times with exponential backoff.
- [ ] Correlation IDs propagate from request through logs and background jobs.
- [ ] API startup is blocked if database migrations are not current.
