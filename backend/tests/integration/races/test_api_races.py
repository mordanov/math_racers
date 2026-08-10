"""Integration tests for POST /api/v1/races/.

Requires the full stack running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def _auth_token() -> str:
    """Log in as the default admin and return an access token."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "adminpassword123")
    resp = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _valid_payload(race_id: str | None = None) -> dict:
    return {
        "race_id": race_id or str(uuid.uuid4()),
        "seed": "42",
        "difficulty_tier": 3,
        "mode": "quick",
        "started_at": "2026-08-10T12:00:00Z",
        "completed_at": "2026-08-10T12:05:00Z",
        "participants": [
            {
                "avatar_id": "avatar-1",
                "position": 1,
                "problems_correct": 8,
                "average_response_ms": 1500,
                "total_distance": 144,
                "xp_earned": 100,
            }
        ],
    }


@pytest.mark.integration
def test_post_race_returns_201_on_valid_payload() -> None:
    token = _auth_token()
    payload = _valid_payload()
    resp = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["race_id"] == payload["race_id"]
    assert "created_at" in body


@pytest.mark.integration
def test_post_race_returns_409_on_duplicate_race_id() -> None:
    token = _auth_token()
    race_id = str(uuid.uuid4())
    payload = _valid_payload(race_id=race_id)

    first = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert first.status_code == 201, first.text

    second = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert second.status_code == 409


@pytest.mark.integration
def test_post_race_returns_422_on_invalid_difficulty_tier() -> None:
    token = _auth_token()
    payload = _valid_payload()
    payload["difficulty_tier"] = 99
    resp = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 422


@pytest.mark.integration
def test_post_race_returns_401_without_auth() -> None:
    payload = _valid_payload()
    resp = httpx.post(
        f"{BASE_URL}/api/v1/races",
        json=payload,
        timeout=10.0,
    )
    assert resp.status_code == 401
