from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.presentation.api.middleware.csrf import CSRFMiddleware

pytestmark = pytest.mark.unit


def _client() -> TestClient:
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)

    @app.post("/api/v1/auth/refresh")
    async def refresh() -> dict[str, bool]:
        return {"ok": True}

    @app.api_route("/api/v1/races", methods=["POST", "PUT", "PATCH", "DELETE"])
    async def create_race() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_refresh_requires_matching_csrf_token_and_allowed_origin() -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().post(
            "/api/v1/auth/refresh",
            headers={
                "Origin": "https://game.example",
                "X-CSRF-Token": "token",
            },
            cookies={"csrf_token": "token"},
        )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "headers,cookies",
    [
        ({"Origin": "https://game.example"}, {}),
        (
            {"Origin": "https://game.example", "X-CSRF-Token": "wrong"},
            {"csrf_token": "token"},
        ),
        (
            {"Origin": "https://attacker.example", "X-CSRF-Token": "token"},
            {"csrf_token": "token"},
        ),
    ],
)
def test_refresh_rejects_missing_mismatched_or_foreign_csrf(
    headers: dict[str, str], cookies: dict[str, str]
) -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().post(
            "/api/v1/auth/refresh",
            headers=headers,
            cookies=cookies,
        )

    assert response.status_code == 403


def test_state_changes_reject_a_foreign_origin() -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().post(
            "/api/v1/races",
            headers={"Origin": "https://attacker.example"},
        )

    assert response.status_code == 403


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_every_state_changing_method_accepts_a_valid_csrf_token(method: str) -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().request(
            method,
            "/api/v1/races",
            headers={
                "Origin": "https://game.example",
                "X-CSRF-Token": "token",
            },
            cookies={"csrf_token": "token"},
        )

    assert response.status_code == 200


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_every_state_changing_method_requires_a_csrf_token(method: str) -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().request(
            method,
            "/api/v1/races",
            headers={"Origin": "https://game.example"},
        )

    assert response.status_code == 403


def test_state_change_rejects_a_missing_origin() -> None:
    with patch(
        "app.presentation.api.middleware.csrf.get_config",
        return_value=SimpleNamespace(CSRF_ALLOWED_ORIGINS="https://game.example"),
    ):
        response = _client().post(
            "/api/v1/races",
            headers={"X-CSRF-Token": "token"},
            cookies={"csrf_token": "token"},
        )

    assert response.status_code == 403
