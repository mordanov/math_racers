"""Integration tests: GET /api/v1/problems.

Requires the stack to be running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.mark.integration
def test_valid_request_returns_200() -> None:
    response = httpx.get(
        f"{BASE_URL}/api/v1/problems", params={"tier": 2, "seed": 1234, "count": 8}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tier"] == 2
    assert body["seed"] == 1234
    assert body["count"] == 8
    assert len(body["problems"]) == 8


@pytest.mark.integration
def test_count_zero_returns_empty_set() -> None:
    response = httpx.get(
        f"{BASE_URL}/api/v1/problems", params={"tier": 1, "seed": 1, "count": 0}
    )
    assert response.status_code == 200
    assert response.json()["problems"] == []


@pytest.mark.integration
def test_tier_out_of_range_returns_422() -> None:
    for tier in (0, 7):
        response = httpx.get(
            f"{BASE_URL}/api/v1/problems", params={"tier": tier, "seed": 1, "count": 5}
        )
        assert response.status_code == 422, f"Expected 422 for tier={tier}"


@pytest.mark.integration
def test_count_out_of_range_returns_422() -> None:
    response = httpx.get(
        f"{BASE_URL}/api/v1/problems", params={"tier": 1, "seed": 1, "count": 101}
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_determinism_across_requests() -> None:
    params = {"tier": 3, "seed": 777, "count": 5}
    a = httpx.get(f"{BASE_URL}/api/v1/problems", params=params).json()["problems"]
    b = httpx.get(f"{BASE_URL}/api/v1/problems", params=params).json()["problems"]
    for pa, pb in zip(a, b):
        assert pa["operation"] == pb["operation"]
        assert pa["operand_a"] == pb["operand_a"]
        assert pa["operand_b"] == pb["operand_b"]
        assert pa["answer"] == pb["answer"]


@pytest.mark.integration
def test_division_answers_are_integers() -> None:
    response = httpx.get(
        f"{BASE_URL}/api/v1/problems", params={"tier": 4, "seed": 42, "count": 100}
    )
    problems = response.json()["problems"]
    for p in problems:
        if p["operation"] == "division":
            assert p["operand_b"] != 0
            assert p["operand_a"] % p["operand_b"] == 0
