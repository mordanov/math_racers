# Sprint 7: Backend Infrastructure Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two remaining backend spec 002 gaps: health endpoint failure-mode tests and correlation ID propagation through background jobs.

**Architecture:** Task 1 adds unit tests for the health router's degraded/unavailable logic by patching the three internal check functions (no real services needed) and one integration test for the X-Request-ID response header. Task 2 threads `request_id_var` from the HTTP request context into the Redis job payload at enqueue time and reads it back in the worker before dispatching, so background job logs carry the originating correlation ID.

**Tech Stack:** Python 3.12, FastAPI, pytest-asyncio, httpx ASGITransport (for in-process health unit tests), redis-py, `infrastructure.logging.request_id_var` / `set_request_id`.

**Spec:** `docs/enhancements/claude-code-tasks.md` §1.3 (T036) and §1.4 (T037–T038)

## Global Constraints

- Python ≥ 3.12; `asyncio_mode = "auto"` in pytest config — no explicit `@pytest.mark.asyncio` needed, but keep `@pytest.mark.unit` on every new unit test.
- `mypy` strict mode must pass after every commit: `cd backend && mypy .`
- `ruff check . && black --check .` must pass after every commit.
- Full unit suite must stay green: `cd backend && pytest -m unit`.
- Do not add new dependencies — `httpx`, `fastapi`, `pytest-asyncio`, and `unittest.mock` are all already available.
- Alembic migrations are NOT needed for either task — no schema changes.

## Review Focus

1. `_enqueue_job` is a sync function that captures `request_id_var.get()` — if that context var was reset between the async handler and the sync enqueue call, the worker gets the nil UUID. Test that the request_id is captured inside `_enqueue_job` (Task 2, Step 1 test).
2. A job payload from an old worker (before this change) has no `"request_id"` key. `process_job` must handle the missing key gracefully rather than raising `KeyError`. Cover this with a test (Task 2, Step 1 test).
3. Health unit tests create a new FastAPI app per test call. `health.py` uses module-level singletons `_db_engine` and `_redis_client`. Patching `_check_database` / `_check_redis` directly bypasses those singletons — confirm the patch target strings are correct before running (`app.presentation.api.v1.health._check_database` etc.).
4. The X-Request-ID integration test requires a running stack. Mark it `@pytest.mark.integration` and add it to the existing `tests/integration/test_health.py`; it will be skipped in the unit suite automatically.
5. `set_request_id` in `worker.py` must be imported at module level (not inside `process_job`) so `patch("app.worker.set_request_id", …)` resolves correctly in tests.

---

### Task 1: Health endpoint failure-mode unit tests

**Files:**
- Create: `backend/tests/unit/test_health.py`
- Modify: `backend/tests/integration/test_health.py` (add one integration test at the bottom)

**Interfaces:**
- Consumes: nothing from Task 2 — fully independent.
- Produces: nothing consumed by Task 2.

---

- [ ] **Step 1: Write the three failing unit tests**

Create `backend/tests/unit/test_health.py` with exactly this content:

```python
"""Unit tests for /health failure modes — no real services required."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.presentation.api.v1.health import router as health_router


def _health_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health_router)
    return app


def _mock_cfg() -> MagicMock:
    cfg = MagicMock()
    cfg.VERSION = "test"
    return cfg


@pytest.mark.unit
async def test_health_degraded_when_redis_unavailable() -> None:
    """Redis down: HTTP 200 with overall status 'degraded'."""
    with (
        patch(
            "app.presentation.api.v1.health._check_database",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health._check_redis",
            new=AsyncMock(return_value="unavailable"),
        ),
        patch(
            "app.presentation.api.v1.health._check_storage",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health.get_config",
            return_value=_mock_cfg(),
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=_health_app()), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "unavailable"


@pytest.mark.unit
async def test_health_unavailable_when_db_down() -> None:
    """Database down: HTTP 503 with overall status 'unavailable'."""
    with (
        patch(
            "app.presentation.api.v1.health._check_database",
            new=AsyncMock(return_value="unavailable"),
        ),
        patch(
            "app.presentation.api.v1.health._check_redis",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health._check_storage",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health.get_config",
            return_value=_mock_cfg(),
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=_health_app()), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["database"] == "unavailable"


@pytest.mark.unit
async def test_health_ok_when_all_services_available() -> None:
    """All services available: HTTP 200 with overall status 'ok'."""
    with (
        patch(
            "app.presentation.api.v1.health._check_database",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health._check_redis",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health._check_storage",
            new=AsyncMock(return_value="ok"),
        ),
        patch(
            "app.presentation.api.v1.health.get_config",
            return_value=_mock_cfg(),
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=_health_app()), base_url="http://test"
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && pytest tests/unit/test_health.py -v
```

Expected: 3 tests collected, all **FAIL** — the health route calls `get_config()` for real (no env vars set in the unit environment), so the `_check_*` patches alone won't help yet. The patching approach will be verified correct once the test file exists and we confirm what they actually fail on. If they unexpectedly pass, recheck the patch target strings match the actual import paths in `health.py`.

> **Note:** If tests pass on first run, the patching strategy is already correct. Skip to Step 5 — no production code change is needed.

- [ ] **Step 3: No production code change needed**

The health endpoint logic is already correct (`_check_database` returning "unavailable" → 503, Redis-only → 200). These are pure test additions verifying existing behaviour. Step 2 may show the tests pass immediately if `get_config` is also successfully mocked — that is acceptable.

- [ ] **Step 4: Add X-Request-ID integration test**

Open `backend/tests/integration/test_health.py` and append at the bottom:

```python
@pytest.mark.integration
def test_health_response_includes_x_request_id_header() -> None:
    """Every /health response carries an X-Request-ID response header."""
    response = httpx.get(HEALTH_URL, timeout=10.0)
    assert "x-request-id" in {k.lower() for k in response.headers}


@pytest.mark.integration
def test_health_echoes_x_request_id_from_request() -> None:
    """Health endpoint echoes back the caller's X-Request-ID header."""
    import uuid as _uuid

    custom_id = str(_uuid.uuid4())
    response = httpx.get(HEALTH_URL, headers={"X-Request-ID": custom_id}, timeout=10.0)
    assert response.headers.get("X-Request-ID") == custom_id
```

- [ ] **Step 5: Run unit suite**

```bash
cd backend && pytest -m unit --tb=short -q
```

Expected: **80 passed** (77 prior + 3 new), 0 failures.

- [ ] **Step 6: Run lint and type checks**

```bash
cd backend && ruff check . && black --check . && mypy .
```

Expected: all clean, no output.

- [ ] **Step 7: Commit**

```bash
cd backend && git add tests/unit/test_health.py tests/integration/test_health.py
git commit -m "test(health): add unit tests for degraded/unavailable states and X-Request-ID integration tests

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Correlation ID propagation in background jobs

**Files:**
- Modify: `backend/app/avatars/domain_service.py` (lines 79–91, `_enqueue_job` function)
- Modify: `backend/app/worker.py` (line 9 import block; lines 22–35, `process_job`)
- Create: `backend/tests/unit/avatars/test_correlation_id_propagation.py`
- Create: `backend/tests/unit/test_worker.py`

**Interfaces:**
- Consumes: nothing from Task 1 — fully independent.
- Produces: `_enqueue_job` now always writes a `"request_id"` key in the Redis JSON payload; `process_job` now always calls `set_request_id(str(rid))` before dispatching.

---

- [ ] **Step 1: Write four failing tests**

Create `backend/tests/unit/avatars/test_correlation_id_propagation.py`:

```python
"""Unit tests — request_id propagation through _enqueue_job."""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.logging import request_id_var


@pytest.mark.unit
def test_enqueue_job_includes_request_id_from_context_var() -> None:
    """_enqueue_job embeds the active request_id in the Redis payload."""
    from app.avatars.domain_service import _enqueue_job

    expected_rid = str(uuid.uuid4())
    token = request_id_var.set(expected_rid)

    captured: list[str] = []
    mock_client = MagicMock()
    mock_client.rpush.side_effect = lambda _key, payload: captured.append(str(payload))

    with patch("redis.from_url", return_value=mock_client):
        _enqueue_job("redis://localhost", uuid.uuid4(), uuid.uuid4())

    request_id_var.reset(token)

    assert len(captured) == 1
    data = json.loads(captured[0])
    assert data["request_id"] == expected_rid


@pytest.mark.unit
def test_enqueue_job_uses_nil_uuid_when_no_request_context() -> None:
    """_enqueue_job uses the nil UUID when no request context is active."""
    from app.avatars.domain_service import _enqueue_job

    captured: list[str] = []
    mock_client = MagicMock()
    mock_client.rpush.side_effect = lambda _key, payload: captured.append(str(payload))

    with patch("redis.from_url", return_value=mock_client):
        _enqueue_job("redis://localhost", uuid.uuid4(), uuid.uuid4())

    data = json.loads(captured[0])
    assert data["request_id"] == "00000000-0000-0000-0000-000000000000"
```

Create `backend/tests/unit/test_worker.py`:

```python
"""Unit tests — process_job correlation ID handling."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.unit
async def test_process_job_sets_request_id_before_dispatch() -> None:
    """process_job sets the request_id context var before calling the handler."""
    from app.worker import process_job

    job_rid = str(uuid.uuid4())
    job: dict[str, object] = {
        "job_type": "avatar_generation",
        "job_id": str(uuid.uuid4()),
        "avatar_id": str(uuid.uuid4()),
        "request_id": job_rid,
    }

    with (
        patch("app.worker.set_request_id") as mock_set_rid,
        patch(
            "app.avatars.generation_service.run_generation_job",
            new=AsyncMock(return_value=None),
        ),
    ):
        await process_job(job)

    mock_set_rid.assert_called_once_with(job_rid)


@pytest.mark.unit
async def test_process_job_tolerates_missing_request_id() -> None:
    """process_job does not raise when job payload has no request_id key."""
    from app.worker import process_job

    job: dict[str, object] = {
        "job_type": "avatar_generation",
        "job_id": str(uuid.uuid4()),
        "avatar_id": str(uuid.uuid4()),
        # no request_id key — simulates a job enqueued before this change
    }

    with patch(
        "app.avatars.generation_service.run_generation_job",
        new=AsyncMock(return_value=None),
    ):
        await process_job(job)  # must not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && pytest tests/unit/avatars/test_correlation_id_propagation.py tests/unit/test_worker.py -v
```

Expected: 4 tests, all **FAIL**:
- `test_enqueue_job_includes_request_id_from_context_var` — FAIL: `KeyError: 'request_id'` (key not in payload)
- `test_enqueue_job_uses_nil_uuid_when_no_request_context` — FAIL: same
- `test_process_job_sets_request_id_before_dispatch` — FAIL: `mock_set_rid` never called (import doesn't exist yet)
- `test_process_job_tolerates_missing_request_id` — may PASS if the current worker silently ignores unknown keys; if so, note it in the ledger and skip the "watch it fail" requirement for that single test only.

- [ ] **Step 3: Add `request_id` to `_enqueue_job` payload**

Edit `backend/app/avatars/domain_service.py`. The current `_enqueue_job` function (lines ~79–91) looks like this:

```python
def _enqueue_job(redis_url: str, job_id: uuid.UUID, avatar_id: uuid.UUID) -> None:
    import redis as _redis

    client = _redis.from_url(redis_url)  # type: ignore[no-untyped-call]
    payload = json.dumps(
        {
            "job_type": "avatar_generation",
            "job_id": str(job_id),
            "avatar_id": str(avatar_id),
        }
    )
    client.rpush("job_queue", payload)
    client.close()
```

Replace it with:

```python
def _enqueue_job(redis_url: str, job_id: uuid.UUID, avatar_id: uuid.UUID) -> None:
    import redis as _redis

    from infrastructure.logging import request_id_var

    client = _redis.from_url(redis_url)  # type: ignore[no-untyped-call]
    payload = json.dumps(
        {
            "job_type": "avatar_generation",
            "job_id": str(job_id),
            "avatar_id": str(avatar_id),
            "request_id": request_id_var.get(),
        }
    )
    client.rpush("job_queue", payload)
    client.close()
```

- [ ] **Step 4: Add `set_request_id` import and call to `worker.py`**

Edit `backend/app/worker.py`. Change the import line at the top from:

```python
from infrastructure.logging import get_logger, setup_logging
```

to:

```python
from infrastructure.logging import get_logger, set_request_id, setup_logging
```

Then modify `process_job` to call `set_request_id` before dispatching. Current function:

```python
async def process_job(job: dict[str, object]) -> None:
    """Dispatch a job to the appropriate handler. Idempotent."""
    import uuid as _uuid

    job_id = job.get("job_id", "unknown")
    job_type = job.get("job_type", "unknown")
    logger.info("Processing job", extra={"context": {"job_id": job_id, "job_type": job_type}})
    ...
```

Replace with:

```python
async def process_job(job: dict[str, object]) -> None:
    """Dispatch a job to the appropriate handler. Idempotent."""
    import uuid as _uuid

    rid = job.get("request_id")
    if rid:
        set_request_id(str(rid))

    job_id = job.get("job_id", "unknown")
    job_type = job.get("job_type", "unknown")
    logger.info("Processing job", extra={"context": {"job_id": job_id, "job_type": job_type}})
    ...
```

(Leave the rest of `process_job` unchanged.)

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend && pytest tests/unit/avatars/test_correlation_id_propagation.py tests/unit/test_worker.py -v
```

Expected: 4 tests, all **PASS**.

- [ ] **Step 6: Run full unit suite**

```bash
cd backend && pytest -m unit --tb=short -q
```

Expected: **84 passed** (80 after Task 1 + 4 new), 0 failures.

- [ ] **Step 7: Run lint and type checks**

```bash
cd backend && ruff check . && black --check . && mypy .
```

Expected: all clean, no output.

- [ ] **Step 8: Commit**

```bash
git add \
  backend/app/avatars/domain_service.py \
  backend/app/worker.py \
  backend/tests/unit/avatars/test_correlation_id_propagation.py \
  backend/tests/unit/test_worker.py
git commit -m "feat(worker): propagate X-Request-ID through job payload into worker context

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
