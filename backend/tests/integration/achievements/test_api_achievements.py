"""Integration tests for achievements.

Requires the full stack running.
Run with: pytest -m integration
"""

from __future__ import annotations

import os
import time
import uuid

import pytest

from tests.integration import httpx_client as httpx
from tests.integration.races.helpers import (
    build_result_payload,
    create_child_and_avatar,
    create_race_session,
    submit_answers,
    submit_result,
)

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


def _post_session_race(
    token: str,
    *,
    problems_correct: int = 5,
    position: int = 1,
    mode: str = "quick",
) -> httpx.Response:
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_session = create_race_session(BASE_URL, token, child_id, avatar_id, mode=mode)
    payload = build_result_payload(
        race_session,
        avatar_id,
        mode=mode,
        problems_correct=problems_correct,
        position=position,
    )
    submit_answers(BASE_URL, token, child_id, str(race_session["race_id"]), payload["answers"])
    return submit_result(BASE_URL, token, child_id, str(race_session["race_id"]), payload)


# ── Scenario 1: first race unlocks first_race ─────────────────────────────────


def test_first_race_achievement_unlocked() -> None:
    token, account_id = _register_and_approve()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_session = create_race_session(BASE_URL, token, child_id, avatar_id)
    payload = build_result_payload(race_session, avatar_id)
    submit_answers(BASE_URL, token, child_id, str(race_session["race_id"]), payload["answers"])
    resp = submit_result(BASE_URL, token, child_id, str(race_session["race_id"]), payload)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert "new_achievements" in body
    keys = [a["key"] for a in body["new_achievements"]]
    assert "first_race" in keys

    # Also appears in the player's unlock list
    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_id}/achievements",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Child-Profile-ID": child_id,
        },
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    unlocked_keys = [a["key"] for a in list_resp.json()["achievements"]]
    assert "first_race" in unlocked_keys


# ── Scenario 2: duplicate race — no duplicate achievement ─────────────────────


def test_duplicate_race_no_duplicate_achievement() -> None:
    token, account_id = _register_and_approve()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_session = create_race_session(BASE_URL, token, child_id, avatar_id)
    payload = build_result_payload(race_session, avatar_id)
    race_id = str(race_session["race_id"])
    submit_answers(BASE_URL, token, child_id, race_id, payload["answers"])
    first = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert first.status_code == 200, first.text
    assert "first_race" in [a["key"] for a in first.json()["new_achievements"]]

    second = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert second.status_code == 200, second.text
    assert second.json() == first.json()

    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_id}/achievements",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Child-Profile-ID": child_id,
        },
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    first_race_entries = [a for a in list_resp.json()["achievements"] if a["key"] == "first_race"]
    assert len(first_race_entries) == 1


# ── Scenario 4: 8/8 correct unlocks first_race and perfect_race ──────────────


def test_perfect_race_and_first_race_both_unlocked() -> None:
    token, _ = _register_and_approve()
    resp = _post_session_race(token, problems_correct=8, position=1)
    assert resp.status_code == 200, resp.text

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
    child_a_id, _ = create_child_and_avatar(BASE_URL, token_a)

    resp = httpx.get(
        f"{BASE_URL}/api/v1/players/{account_b_id}/achievements",
        headers={
            "Authorization": f"Bearer {token_a}",
            "X-Child-Profile-ID": child_a_id,
        },
        timeout=10.0,
    )
    assert resp.status_code == 403
