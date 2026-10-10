"""Integration tests for the race session and result API.

Requires the full stack running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import base64
import json
import os
import time
import uuid

import pytest

from app.mathematics.generator import generate_problem_set
from app.mathematics.tiers import TierConfig
from app.mathematics.types import Operation
from tests.integration import httpx_client as httpx
from tests.integration.races.helpers import (
    RaceSetupData,
    build_result_payload,
    create_child_and_avatar,
    create_race_session,
    mutation_headers,
    submit_answers,
    submit_result,
)

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def _auth_token() -> str:
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "adminpassword123")
    admin_response = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password},
        headers=mutation_headers(BASE_URL),
        timeout=10.0,
    )
    assert admin_response.status_code == 200, f"Login failed: {admin_response.text}"
    admin_token = str(admin_response.json()["access_token"])

    email = f"race-integ-{uuid.uuid4().hex[:8]}@example.com"
    password = "race-test-password123"
    registration = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": password},
        headers=mutation_headers(BASE_URL),
        timeout=10.0,
    )
    assert registration.status_code == 201, registration.text
    time.sleep(0.2)

    pending_accounts = httpx.get(
        f"{BASE_URL}/api/v1/admin/accounts",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert pending_accounts.status_code == 200, pending_accounts.text
    account_id = next(
        (
            account["id"]
            for account in pending_accounts.json()["items"]
            if account["email"] == email
        ),
        None,
    )
    assert account_id is not None
    approval = httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers=mutation_headers(BASE_URL, admin_token),
        timeout=10.0,
    )
    assert approval.status_code == 200, approval.text

    login = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        headers=mutation_headers(BASE_URL),
        timeout=10.0,
    )
    assert login.status_code == 200, login.text
    return str(login.json()["access_token"])


def _new_race(token: str) -> tuple[str, str, RaceSetupData]:
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    session = create_race_session(BASE_URL, token, child_id, avatar_id)
    result = build_result_payload(session, avatar_id)
    submit_answers(BASE_URL, token, child_id, session["race_id"], result["answers"])
    return child_id, avatar_id, {"session": session, "result": result}


@pytest.mark.integration
def test_post_race_creates_session_with_server_seed() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    response = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json={
            "mode": "quick",
            "difficulty_tier": 3,
            "avatar_id": avatar_id,
            "opponent_count": 0,
        },
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )
    assert response.status_code == 201, response.text
    assert uuid.UUID(response.json()["race_id"])
    assert isinstance(response.json()["seed"], int)


@pytest.mark.integration
def test_result_retry_replays_once_and_conflicting_retry_is_rejected() -> None:
    token = _auth_token()
    child_id, _avatar_id, data = _new_race(token)
    session = data["session"]
    payload = data["result"]
    race_id = str(session["race_id"])

    first = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert first.status_code == 200, first.text
    second = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert second.status_code == 200, second.text
    assert second.json() == first.json()

    payload["idempotency_key"] = str(uuid.uuid4())
    conflict = submit_result(BASE_URL, token, child_id, race_id, payload)
    assert conflict.status_code == 409, conflict.text


@pytest.mark.integration
def test_result_rejects_a_different_child_profile() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    other_child_id, _ = create_child_and_avatar(BASE_URL, token)
    session = create_race_session(BASE_URL, token, child_id, avatar_id)
    payload = build_result_payload(session, avatar_id)

    response = submit_result(
        BASE_URL,
        token,
        other_child_id,
        str(session["race_id"]),
        payload,
    )
    assert response.status_code == 403, response.text


@pytest.mark.integration
def test_human_receives_xp_when_ai_wins_the_race() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    session = create_race_session(
        BASE_URL,
        token,
        child_id,
        avatar_id,
        opponent_count=1,
    )
    payload = build_result_payload(
        session,
        avatar_id,
        problems_correct=0,
        position=2,
    )
    payload["participants"].append({"avatar_id": "ai-1", "position": 1})
    submit_answers(BASE_URL, token, child_id, session["race_id"], payload["answers"])

    response = submit_result(BASE_URL, token, child_id, session["race_id"], payload)

    assert response.status_code == 200, response.text
    progression = response.json()["progression"]
    assert progression["xp_earned_this_race"] == 100
    assert progression["total_xp"] == 100


@pytest.mark.integration
def test_operation_summaries_use_saved_race_answers() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    for difficulty_tier, problems_correct in ((3, 8), (4, 0)):
        session = create_race_session(
            BASE_URL,
            token,
            child_id,
            avatar_id,
            difficulty_tier=difficulty_tier,
        )
        payload = build_result_payload(
            session,
            avatar_id,
            difficulty_tier=difficulty_tier,
            problems_correct=problems_correct,
        )
        submit_answers(BASE_URL, token, child_id, session["race_id"], payload["answers"])
        result = submit_result(BASE_URL, token, child_id, session["race_id"], payload)
        assert result.status_code == 200, result.text

    child_headers = {
        "Authorization": f"Bearer {token}",
        "X-Child-Profile-ID": child_id,
    }
    stats = httpx.get(
        f"{BASE_URL}/api/v1/players/me/statistics",
        headers=child_headers,
        timeout=10.0,
    )
    assert stats.status_code == 200, stats.text
    assert stats.json()["favourite_operation"] == "division"
    assert stats.json()["total_races"] == 2
    assert stats.json()["total_problems_solved"] == 16

    weekly = httpx.get(
        f"{BASE_URL}/api/v1/players/me/weekly-summary",
        headers=child_headers,
        timeout=10.0,
    )
    assert weekly.status_code == 200, weekly.text
    assert weekly.json()["strongest_operation"] == "multiplication"
    assert weekly.json()["weakest_operation"] == "division"
    assert weekly.json()["correct_answers"] == 8


@pytest.mark.integration
def test_answer_submission_uses_server_time_and_replays_an_exact_retry() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    session = create_race_session(BASE_URL, token, child_id, avatar_id)
    first_problem = generate_problem_set(2, session["seed"], 8).problems[0]
    answer_request = {
        "answer_index": 0,
        "operation": first_problem.operation.value,
        "answer": str(first_problem.answer),
    }
    url = f"{BASE_URL}/api/v1/races/{session['race_id']}/answers"

    first = httpx.post(
        url,
        json=answer_request,
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )
    retry = httpx.post(
        url,
        json=answer_request,
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )

    assert first.status_code == 200, first.text
    assert retry.status_code == 200, retry.text
    assert retry.json() == first.json()
    assert first.json()["is_correct"] is True
    assert first.json()["response_time_ms"] >= 0

    rejected = httpx.post(
        url,
        json={**answer_request, "response_time_ms": 0},
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )
    assert rejected.status_code == 422


@pytest.mark.integration
def test_tier6_session_uses_saved_parent_settings() -> None:
    token = _auth_token()
    payload = token.split(".")[1]
    account_id = str(
        json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["sub"]
    )
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    settings = {
        "custom_tier_config": {
            "operations": ["division"],
            "min_operand": 2,
            "max_operand": 30,
        }
    }
    saved = httpx.patch(
        f"{BASE_URL}/api/v1/players/{account_id}/tier-6-settings",
        json=settings,
        headers=mutation_headers(BASE_URL, token),
        timeout=10.0,
    )
    assert saved.status_code == 200, saved.text
    session = create_race_session(BASE_URL, token, child_id, avatar_id, difficulty_tier=6)
    config = TierConfig(tier=6, operations=(Operation.division,), min_operand=2, max_operand=30)
    problem = generate_problem_set(6, session["seed"], 8, config).problems[0]

    wrong_operation = httpx.post(
        f"{BASE_URL}/api/v1/races/{session['race_id']}/answers",
        json={"answer_index": 0, "operation": "addition", "answer": str(problem.answer)},
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )
    assert wrong_operation.status_code == 422
    accepted = httpx.post(
        f"{BASE_URL}/api/v1/races/{session['race_id']}/answers",
        json={
            "answer_index": 0,
            "operation": problem.operation.value,
            "answer": str(problem.answer),
        },
        headers=mutation_headers(BASE_URL, token, child_id),
        timeout=10.0,
    )
    assert accepted.status_code == 200, accepted.text


@pytest.mark.integration
def test_create_race_session_rejects_invalid_tier() -> None:
    token = _auth_token()
    child_id, avatar_id = create_child_and_avatar(BASE_URL, token)
    response = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json={
            "mode": "quick",
            "difficulty_tier": 99,
            "avatar_id": avatar_id,
            "opponent_count": 0,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Child-Profile-ID": child_id,
        },
        timeout=10.0,
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_create_race_requires_authentication() -> None:
    response = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json={
            "mode": "quick",
            "difficulty_tier": 2,
            "avatar_id": str(uuid.uuid4()),
            "opponent_count": 0,
        },
        headers={"X-Child-Profile-ID": str(uuid.uuid4())},
        timeout=10.0,
    )
    assert response.status_code == 401
