"""Integration tests for XP progression endpoints.

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

pytestmark = pytest.mark.integration


def _login(email: str, password: str) -> str:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _register_and_approve() -> str:
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    email = f"prog-integ-{uuid.uuid4().hex[:8]}@example.com"
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


def _post_race(
    token: str,
    *,
    race_id: str | None = None,
    problems_correct: int = 7,
    longest_streak: int = 5,
    mode: str = "quick",
) -> httpx.Response:
    return httpx.post(
        f"{BASE_URL}/api/v1/races",
        json={
            "race_id": race_id or str(uuid.uuid4()),
            "seed": "42",
            "difficulty_tier": 2,
            "mode": mode,
            "started_at": "2026-08-12T10:00:00Z",
            "completed_at": "2026-08-12T10:05:00Z",
            "participants": [
                {
                    "avatar_id": "a1",
                    "position": 1,
                    "problems_correct": problems_correct,
                    "longest_streak": longest_streak,
                    "average_response_ms": 1200,
                    "total_distance": 126,
                    "xp_earned": 70,
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )


# ── US1: Earn XP after a race ─────────────────────────────────────────────────


def test_xp_awarded_on_race_submission() -> None:
    token = _register_and_approve()
    resp = _post_race(token, problems_correct=7, longest_streak=5, mode="quick")
    assert resp.status_code == 201, resp.text
    body = resp.json()

    assert "progression" in body
    prog = body["progression"]
    # 100 (race) + 7*20 (correct) + floor(5/5)*10 (streak) = 100+140+10 = 250
    assert prog["xp_earned_this_race"] == 250
    assert prog["total_xp"] == 250
    assert prog["current_level"] == 1
    assert prog["level_up"] is not None
    assert prog["level_up"]["previous_level"] == 0
    assert prog["level_up"]["new_level"] == 1


def test_duplicate_race_returns_409_and_no_double_xp() -> None:
    token = _register_and_approve()
    race_id = str(uuid.uuid4())

    first = _post_race(token, race_id=race_id, problems_correct=0, longest_streak=0)
    assert first.status_code == 201, first.text
    first_xp = first.json()["progression"]["total_xp"]

    second = _post_race(token, race_id=race_id, problems_correct=0, longest_streak=0)
    assert second.status_code == 409, second.text

    get_resp = httpx.get(
        f"{BASE_URL}/api/v1/progression",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["total_xp"] == first_xp


# ── US2: View current progression ────────────────────────────────────────────


def test_get_progression_zero_state() -> None:
    token = _register_and_approve()
    resp = httpx.get(
        f"{BASE_URL}/api/v1/progression",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_xp"] == 0
    assert body["current_level"] == 0
    assert body["xp_to_next_level"] == 100


def test_get_progression_after_race() -> None:
    token = _register_and_approve()
    race_resp = _post_race(token, problems_correct=7, longest_streak=5)
    assert race_resp.status_code == 201, race_resp.text
    race_prog = race_resp.json()["progression"]

    get_resp = httpx.get(
        f"{BASE_URL}/api/v1/progression",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert get_resp.status_code == 200
    get_prog = get_resp.json()
    assert get_prog["total_xp"] == race_prog["total_xp"]
    assert get_prog["current_level"] == race_prog["current_level"]
    assert get_prog["xp_to_next_level"] == race_prog["xp_to_next_level"]


def test_progression_unauthenticated() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/progression", timeout=10.0)
    assert resp.status_code == 401


# ── US3: Championship race bonus XP ──────────────────────────────────────────


def test_championship_bonus_xp() -> None:
    token = _register_and_approve()
    resp = _post_race(token, problems_correct=5, longest_streak=0, mode="championship")
    assert resp.status_code == 201, resp.text
    prog = resp.json()["progression"]
    # 100 (race) + 5*20 (correct) + 0 (streak) + 500 (championship) = 700
    assert prog["xp_earned_this_race"] == 700
