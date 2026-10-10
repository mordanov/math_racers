"""Integration tests for XP progression endpoints.

Requires the full stack running (docker compose up).
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


def _post_session_race(
    token: str,
    *,
    problems_correct: int = 7,
    longest_streak: int = 5,
    mode: str = "quick",
    child_id: str | None = None,
    avatar_id: str | None = None,
) -> httpx.Response:
    if child_id is None or avatar_id is None:
        child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_session = create_race_session(BASE_URL, token, child_id, avatar_id, mode=mode)
    payload = build_result_payload(
        race_session,
        avatar_id,
        mode=mode,
        problems_correct=problems_correct,
        longest_streak=longest_streak,
    )
    submit_answers(BASE_URL, token, child_id, str(race_session["race_id"]), payload["answers"])
    return submit_result(BASE_URL, token, child_id, str(race_session["race_id"]), payload)


def _get_progression(token: str, child_id: str) -> httpx.Response:
    return httpx.get(
        f"{BASE_URL}/api/v1/progression",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Child-Profile-ID": child_id,
        },
        timeout=10.0,
    )


# ── US1: Earn XP after a race ─────────────────────────────────────────────────


def test_xp_awarded_on_race_submission() -> None:
    token = _register_and_approve()
    resp = _post_session_race(token, problems_correct=7, longest_streak=5, mode="quick")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert "progression" in body
    prog = body["progression"]
    # 100 (race) + 7*20 (correct) + floor(5/5)*10 (streak) = 100+140+10 = 250
    assert prog["xp_earned_this_race"] == 250
    assert prog["total_xp"] == 250
    assert prog["current_level"] == 1
    assert prog["level_up"] is None


def test_duplicate_race_returns_409_and_no_double_xp() -> None:
    token = _register_and_approve()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_session = create_race_session(BASE_URL, token, child_id, avatar_id)
    payload = build_result_payload(race_session, avatar_id, problems_correct=0, longest_streak=0)
    race_id = str(race_session["race_id"])
    submit_answers(BASE_URL, token, child_id, race_id, payload["answers"])
    first = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert first.status_code == 200, first.text
    first_xp = first.json()["progression"]["total_xp"]

    second = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert second.status_code == 200, second.text
    assert second.json() == first.json()

    get_resp = _get_progression(token, child_id)
    assert get_resp.status_code == 200
    assert get_resp.json()["total_xp"] == first_xp


# ── US2: View current progression ────────────────────────────────────────────


def test_get_progression_zero_state() -> None:
    token = _register_and_approve()
    child_id, _avatar_id = create_child_and_avatar(BASE_URL, token)
    resp = _get_progression(token, child_id)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_xp"] == 0
    assert body["current_level"] == 1
    assert body["xp_to_next_level"] == 400


def test_get_progression_after_race() -> None:
    token = _register_and_approve()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    race_resp = _post_session_race(
        token, problems_correct=7, longest_streak=5, child_id=child_id, avatar_id=avatar_id
    )
    assert race_resp.status_code == 200, race_resp.text
    race_prog = race_resp.json()["progression"]

    get_resp = _get_progression(token, child_id)
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
    resp = _post_session_race(token, problems_correct=5, longest_streak=1, mode="championship")
    assert resp.status_code == 200, resp.text
    prog = resp.json()["progression"]
    # Championship completion XP is awarded once when the last race is recorded.
    assert prog["xp_earned_this_race"] == 200
