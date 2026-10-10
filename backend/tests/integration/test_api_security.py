from __future__ import annotations

import os
import uuid

import httpx
import pytest

from tests.integration import httpx_client

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.mark.integration
def test_state_change_without_csrf_is_rejected() -> None:
    response = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": f"csrf-{uuid.uuid4().hex}@example.com", "password": "securepassword123"},
        timeout=10.0,
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_login_rate_limit_returns_429() -> None:
    statuses = [
        httpx_client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": f"unknown-{index}@example.com", "password": "not-a-password"},
            timeout=10.0,
        ).status_code
        for index in range(21)
    ]

    assert statuses[:20] == [403] * 20
    assert statuses[20] == 429


@pytest.mark.integration
def test_registration_rate_limit_returns_429() -> None:
    statuses = [
        httpx_client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": f"register-{uuid.uuid4().hex}@example.com",
                "password": "securepassword123",
            },
            timeout=10.0,
        ).status_code
        for _ in range(4)
    ]

    assert statuses == [201, 201, 201, 429]
