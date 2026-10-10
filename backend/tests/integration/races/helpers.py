from __future__ import annotations

import uuid
from typing import TypedDict
from urllib.parse import urlsplit

from app.mathematics.generator import generate_problem_set
from tests.integration import httpx_client as httpx


class RaceSession(TypedDict):
    race_id: str
    seed: int


class AnswerPayload(TypedDict):
    operation: str
    answer: str
    response_time_ms: int


class RaceParticipant(TypedDict):
    avatar_id: str
    position: int | None


class RaceResultPayload(TypedDict):
    idempotency_key: str
    human_avatar_id: str
    participants: list[RaceParticipant]
    answers: list[AnswerPayload]


class RaceSetupData(TypedDict):
    session: RaceSession
    result: RaceResultPayload


def mutation_headers(
    base_url: str, token: str | None = None, child_id: str | None = None
) -> dict[str, str]:
    response = httpx.get(f"{base_url}/api/v1/auth/csrf", timeout=10.0)
    assert response.status_code == 204, response.text
    csrf_token = response.cookies.get("csrf_token")
    assert csrf_token
    parsed_origin = urlsplit(base_url)
    headers = {
        "Origin": f"{parsed_origin.scheme}://{parsed_origin.netloc}",
        "Cookie": f"csrf_token={csrf_token}",
        "X-CSRF-Token": csrf_token,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if child_id:
        headers["X-Child-Profile-ID"] = child_id
    return headers


def create_child_and_avatar(base_url: str, token: str) -> tuple[str, str]:
    headers = mutation_headers(base_url, token)
    child_response = httpx.post(
        f"{base_url}/api/v1/child-profiles",
        json={"display_name": "Test Child"},
        headers=headers,
        timeout=10.0,
    )
    assert child_response.status_code == 201, child_response.text
    child_data = child_response.json()
    assert isinstance(child_data, dict)
    child_id = child_data.get("id")
    assert isinstance(child_id, str)

    avatar_response = httpx.post(
        f"{base_url}/api/v1/avatars",
        json={"species": "fox"},
        headers={**headers, "X-Child-Profile-ID": child_id},
        timeout=10.0,
    )
    assert avatar_response.status_code == 201, avatar_response.text
    avatar_data = avatar_response.json()
    assert isinstance(avatar_data, dict)
    avatar_id = avatar_data.get("avatar_id")
    assert isinstance(avatar_id, str)
    return child_id, avatar_id


def create_race_session(
    base_url: str,
    token: str,
    child_id: str,
    avatar_id: str,
    *,
    mode: str = "quick",
    difficulty_tier: int = 2,
    opponent_count: int = 0,
    championship_id: str | None = None,
) -> RaceSession:
    body: dict[str, object] = {
        "mode": mode,
        "difficulty_tier": difficulty_tier,
        "avatar_id": avatar_id,
        "opponent_count": opponent_count,
    }
    if championship_id is not None:
        body["championship_id"] = championship_id
    elif mode == "championship":
        championship_response = httpx.post(
            f"{base_url}/api/v1/championships",
            json={"total_races": 3},
            headers=mutation_headers(base_url, token, child_id),
            timeout=10.0,
        )
        assert championship_response.status_code == 201, championship_response.text
        body["championship_id"] = championship_response.json()["championship_id"]
    response = httpx.post(
        f"{base_url}/api/v1/races",
        json=body,
        headers=mutation_headers(base_url, token, child_id),
        timeout=10.0,
    )
    assert response.status_code == 201, response.text
    response_data = response.json()
    assert isinstance(response_data, dict)
    race_id = response_data.get("race_id")
    seed = response_data.get("seed")
    assert isinstance(race_id, str)
    assert isinstance(seed, int)
    return {"race_id": race_id, "seed": seed}


def build_result_payload(
    session: RaceSession,
    avatar_id: str,
    *,
    mode: str = "quick",
    difficulty_tier: int = 2,
    problems_correct: int = 8,
    position: int | None = 1,
    longest_streak: int | None = None,
) -> RaceResultPayload:
    answer_count = 8 if mode != "training" else problems_correct
    if longest_streak is None:
        longest_streak = problems_correct
    correct_flags = [True] * longest_streak
    if longest_streak < problems_correct:
        correct_flags.append(False)
        correct_flags.extend([True] * (problems_correct - longest_streak))
    correct_flags.extend([False] * (answer_count - len(correct_flags)))
    problems = generate_problem_set(difficulty_tier, session["seed"], answer_count).problems
    answers: list[AnswerPayload] = [
        {
            "operation": problem.operation.value,
            "answer": str(problem.answer if correct_flags[index] else problem.answer + 1),
            "response_time_ms": 1500,
        }
        for index, problem in enumerate(problems)
    ]
    return {
        "idempotency_key": str(uuid.uuid4()),
        "human_avatar_id": avatar_id,
        "participants": [
            {
                "avatar_id": avatar_id,
                "position": position,
            }
        ],
        "answers": answers,
    }


def submit_answers(
    base_url: str, token: str, child_id: str, race_id: str, answers: list[AnswerPayload]
) -> None:
    for index, answer in enumerate(answers):
        response = httpx.post(
            f"{base_url}/api/v1/races/{race_id}/answers",
            json={
                "answer_index": index,
                "operation": answer["operation"],
                "answer": answer["answer"],
            },
            headers=mutation_headers(base_url, token, child_id),
            timeout=10.0,
        )
        assert response.status_code == 200, response.text


def submit_result(
    base_url: str,
    token: str,
    child_id: str,
    race_id: str,
    payload: RaceResultPayload,
) -> httpx.Response:
    result_body = {
        "idempotency_key": payload["idempotency_key"],
        "human_avatar_id": payload["human_avatar_id"],
        "participants": payload["participants"],
    }
    return httpx.post(
        f"{base_url}/api/v1/races/{race_id}/results",
        json=result_body,
        headers=mutation_headers(base_url, token, child_id),
        timeout=10.0,
    )
