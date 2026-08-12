"""Integration tests for championship endpoints.

Requires the full stack running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import os
import time
import uuid

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword123")


def _login(email: str, password: str) -> str:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _register_and_approve() -> str:
    """Register, approve, and return a token for a fresh account."""
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    email = f"champ-integ-{uuid.uuid4().hex[:8]}@example.com"
    password = "password123!"

    reg = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert reg.status_code == 201

    time.sleep(0.2)
    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/admin/accounts",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    account_id = next((i["id"] for i in items if i["email"] == email), None)
    assert account_id is not None

    approve = httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert approve.status_code == 200
    time.sleep(0.2)
    return _login(email, password)


def _post_race(token: str, mode: str = "championship") -> str:
    """Submit a race and return its race_id."""
    race_id = str(uuid.uuid4())
    resp = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json={
            "race_id": race_id,
            "seed": "42",
            "difficulty_tier": 2,
            "mode": mode,
            "started_at": "2026-08-10T10:00:00Z",
            "completed_at": "2026-08-10T10:05:00Z",
            "participants": [
                {
                    "avatar_id": "a1",
                    "position": 1,
                    "problems_correct": 7,
                    "longest_streak": 0,
                    "average_response_ms": 1200,
                    "total_distance": 126,
                    "xp_earned": 70,
                },
                {
                    "avatar_id": "a2",
                    "position": 2,
                    "problems_correct": 5,
                    "longest_streak": 0,
                    "average_response_ms": 1800,
                    "total_distance": 90,
                    "xp_earned": 50,
                },
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 201, resp.text
    return race_id


@pytest.mark.integration
def test_create_championship_returns_201() -> None:
    token = _register_and_approve()
    resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["total_races"] == 3
    assert body["races_completed"] == 0
    assert body["status"] == "active"
    assert body["standings"] == []


@pytest.mark.integration
def test_create_championship_returns_401_without_auth() -> None:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        timeout=10.0,
    )
    assert resp.status_code == 401


@pytest.mark.integration
def test_create_championship_returns_422_for_invalid_total_races() -> None:
    token = _register_and_approve()
    resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 2},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 422


@pytest.mark.integration
def test_get_championship_returns_current_state() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    champ_id = create_resp.json()["championship_id"]

    get_resp = httpx.get(
        f"{BASE_URL}/api/v1/championships/{champ_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["championship_id"] == champ_id


@pytest.mark.integration
def test_get_championship_returns_403_for_other_account() -> None:
    owner_token = _register_and_approve()
    other_token = _register_and_approve()

    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        headers={"Authorization": f"Bearer {owner_token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    champ_id = create_resp.json()["championship_id"]

    get_resp = httpx.get(
        f"{BASE_URL}/api/v1/championships/{champ_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        timeout=10.0,
    )
    assert get_resp.status_code == 403


@pytest.mark.integration
def test_patch_race_updates_standings_and_auto_completes() -> None:
    token = _register_and_approve()

    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    champ_id = create_resp.json()["championship_id"]

    for race_index in range(3):
        race_id = _post_race(token)
        patch_resp = httpx.patch(
            f"{BASE_URL}/api/v1/championships/{champ_id}/races/{race_id}",
            json={
                "race_index": race_index,
                "participants": [
                    {"avatar_id": "a1", "is_player": True, "finishing_position": 1},
                    {"avatar_id": "a2", "is_player": False, "finishing_position": 2},
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert patch_resp.status_code == 200, patch_resp.text
        body = patch_resp.json()
        assert body["races_completed"] == race_index + 1

    assert body["status"] == "completed"
    standings = body["standings"]
    assert standings[0]["avatar_id"] == "a1"
    assert standings[0]["points"] == 30
    assert standings[0]["position"] == 1


@pytest.mark.integration
def test_patch_race_returns_409_on_duplicate_race_id() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/championships",
        json={"total_races": 3},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201, create_resp.text
    champ_id = create_resp.json()["championship_id"]
    race_id = _post_race(token)

    patch_body = {
        "race_index": 0,
        "participants": [
            {"avatar_id": "a1", "is_player": True, "finishing_position": 1}
        ],
    }
    first = httpx.patch(
        f"{BASE_URL}/api/v1/championships/{champ_id}/races/{race_id}",
        json=patch_body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert first.status_code == 200, first.text

    second = httpx.patch(
        f"{BASE_URL}/api/v1/championships/{champ_id}/races/{race_id}",
        json=patch_body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert second.status_code == 409
