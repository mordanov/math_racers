"""Shared fixtures for integration tests under tests/integration/api/.

Requires the full stack running (docker compose up).
"""

from __future__ import annotations

import os
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


@pytest.fixture(scope="module")
def parent_token() -> str:
    """Register, approve, and log in a fresh parent account; return its access token."""
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)

    email = f"parent-integ-{uuid.uuid4().hex[:8]}@example.com"
    reg = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": "parentpassword123"},
        timeout=10.0,
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"

    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/admin/accounts",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    account_id = next((item["id"] for item in items if item["email"] == email), None)
    assert account_id is not None, f"Could not find pending account for {email}"

    approve = httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert approve.status_code == 200, f"Approve failed: {approve.text}"

    return _login(email, "parentpassword123")


@pytest.fixture(scope="module")
def player_id(parent_token: str) -> str:
    """Return the account ID of the parent whose token is parent_token.

    Obtains it via the admin account list by matching the token's sub claim.
    Uses the JWT payload directly to avoid an extra endpoint dependency.
    """
    import base64
    import json

    parts = parent_token.split(".")
    assert len(parts) == 3, "Malformed JWT"
    payload_b64 = parts[1] + "=="
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    return str(payload["sub"])
