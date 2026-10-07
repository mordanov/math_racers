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
            transport=ASGITransport(app=_health_app()),  # type: ignore[arg-type]
            base_url="http://test",
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
            transport=ASGITransport(app=_health_app()),  # type: ignore[arg-type]
            base_url="http://test",
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
            transport=ASGITransport(app=_health_app()),  # type: ignore[arg-type]
            base_url="http://test",
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
