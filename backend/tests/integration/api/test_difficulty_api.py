"""Integration tests: GET/PATCH /api/v1/players/{id}/difficulty.

Requires the stack to be running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_unauthenticated_get_returns_401(player_id: str = "00000000-0000-0000-0000-000000000001") -> None:
    response = httpx.get(f"{BASE_URL}/api/v1/players/{player_id}/difficulty")
    assert response.status_code == 401


@pytest.mark.integration
def test_unknown_player_returns_404(parent_token: str) -> None:
    fake_id = "00000000-0000-0000-0000-000000000099"
    response = httpx.get(
        f"{BASE_URL}/api/v1/players/{fake_id}/difficulty",
        headers=_auth_headers(parent_token),
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_patch_sets_parent_override(parent_token: str, player_id: str) -> None:
    response = httpx.patch(
        f"{BASE_URL}/api/v1/players/{player_id}/difficulty",
        json={"parent_override": 4},
        headers=_auth_headers(parent_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["parent_override"] == 4
    assert body["effective_tier"] == 4


@pytest.mark.integration
def test_patch_clears_parent_override(parent_token: str, player_id: str) -> None:
    httpx.patch(
        f"{BASE_URL}/api/v1/players/{player_id}/difficulty",
        json={"parent_override": 3},
        headers=_auth_headers(parent_token),
    )
    response = httpx.patch(
        f"{BASE_URL}/api/v1/players/{player_id}/difficulty",
        json={"parent_override": None},
        headers=_auth_headers(parent_token),
    )
    assert response.status_code == 200
    assert response.json()["parent_override"] is None


@pytest.mark.integration
def test_patch_out_of_range_returns_422(parent_token: str, player_id: str) -> None:
    response = httpx.patch(
        f"{BASE_URL}/api/v1/players/{player_id}/difficulty",
        json={"parent_override": 7},
        headers=_auth_headers(parent_token),
    )
    assert response.status_code == 422
