"""Integration test: health endpoint with full Docker Compose stack.

Requires the stack to be running (docker compose up).
Run with: pytest -m integration
"""

import os
import time

import httpx
import pytest


HEALTH_URL = os.getenv("HEALTH_URL", "http://localhost/health")


@pytest.mark.integration
def test_health_returns_ok() -> None:
    """GET /health returns 200 with status=ok when all services are running."""
    response = httpx.get(HEALTH_URL, timeout=10.0)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "ok"


@pytest.mark.integration
def test_health_includes_version() -> None:
    """version field matches the VERSION environment variable."""
    expected_version = os.getenv("VERSION", "")
    response = httpx.get(HEALTH_URL, timeout=10.0)
    body = response.json()
    assert "version" in body
    if expected_version:
        assert body["version"] == expected_version


@pytest.mark.integration
def test_health_response_time() -> None:
    """Health endpoint responds within 100 ms."""
    start = time.monotonic()
    response = httpx.get(HEALTH_URL, timeout=5.0)
    elapsed_ms = (time.monotonic() - start) * 1000
    assert response.status_code in (200, 503)
    assert elapsed_ms < 100, f"Health check took {elapsed_ms:.1f}ms, expected < 100ms"


@pytest.mark.integration
def test_health_has_all_required_fields() -> None:
    """Response body contains all fields defined in the health API contract."""
    response = httpx.get(HEALTH_URL, timeout=10.0)
    body = response.json()
    assert "status" in body
    assert "version" in body
    assert "checks" in body
    assert "database" in body["checks"]
    assert "redis" in body["checks"]
    assert "storage" in body["checks"]


@pytest.mark.integration
def test_health_requires_no_auth() -> None:
    """Health endpoint must be accessible without an Authorization header."""
    response = httpx.get(HEALTH_URL, timeout=10.0, headers={})
    assert response.status_code != 401
    assert response.status_code != 403
