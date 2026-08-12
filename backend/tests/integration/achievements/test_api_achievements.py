"""Integration tests for achievements.

Requires the full stack running.
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


def _register_and_approve() -> tuple[str, str]:
    """Returns (token, account_id)."""
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    email = f"ach-integ-{uuid.uuid4().hex[:8]}@example.com"
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
    token = _login(email, password)
    return token, account_id


def _post_race(
    token: str,
    *,
    race_id: str | None = None,
    problems_correct: int = 5,
    position: int = 1,
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
                    "position": position,
                    "problems_correct": problems_correct,
                    "longest_streak": 0,
                    "average_response_ms": 1200,
                    "total_distance": 126,
                    "xp_earned": 70,
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )


# ── Scenario 1: first race unlocks first_race ─────────────────────────────────


def test_first_race_achievement_unlocked() -> None:
    token, account_id = _register_and_approve()
    resp = _post_race(token)
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert "new_achievements" in body
    keys = [a["key"] for a in body["new_achievements"]]
    assert "first_race" in keys

    # Also appears in the player's unlock list
    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_id}/achievements",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    unlocked_keys = [a["key"] for a in list_resp.json()["achievements"]]
    assert "first_race" in unlocked_keys


# ── Scenario 2: duplicate race — no duplicate achievement ─────────────────────


def test_duplicate_race_no_duplicate_achievement() -> None:
    token, account_id = _register_and_approve()
    race_id = str(uuid.uuid4())

    first = _post_race(token, race_id=race_id)
    assert first.status_code == 201, first.text
    assert "first_race" in [a["key"] for a in first.json()["new_achievements"]]

    second = _post_race(token, race_id=race_id)
    assert second.status_code == 409, second.text

    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_id}/achievements",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    first_race_entries = [a for a in list_resp.json()["achievements"] if a["key"] == "first_race"]
    assert len(first_race_entries) == 1


# ── Scenario 4: 8/8 correct unlocks first_race and perfect_race ──────────────


def test_perfect_race_and_first_race_both_unlocked() -> None:
    token, _ = _register_and_approve()
    resp = _post_race(token, problems_correct=8, position=1)
    assert resp.status_code == 201, resp.text

    keys = [a["key"] for a in resp.json()["new_achievements"]]
    assert "first_race" in keys
    assert "perfect_race" in keys


# ── Scenario 3: hidden achievement invisible until unlocked ───────────────────


def test_hidden_achievement_absent_from_catalogue() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/achievements", timeout=10.0)
    assert resp.status_code == 200
    keys = [a["key"] for a in resp.json()["achievements"]]
    assert "hidden_speedster" not in keys


def test_catalogue_returns_visible_achievements() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/achievements", timeout=10.0)
    assert resp.status_code == 200
    keys = [a["key"] for a in resp.json()["achievements"]]
    assert "first_race" in keys
    assert "perfect_race" in keys


# ── Scenario 6: 403 when requesting another player's achievements ─────────────


def test_cannot_view_another_players_achievements() -> None:
    token_a, _ = _register_and_approve()
    _, account_b_id = _register_and_approve()

    resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_b_id}/achievements",
        headers={"Authorization": f"Bearer {token_a}"},
        timeout=10.0,
    )
    assert resp.status_code == 403
