"""Integration tests for child profiles API endpoints.

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


def _login(email: str, password: str) -> str:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _register_and_approve(admin_token: str) -> str:
    """Register a new parent, approve it, and return its access token."""
    email = f"parent-cp-{uuid.uuid4().hex[:8]}@example.com"
    reg = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": "parentpassword123"},
        timeout=10.0,
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
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
    assert account_id is not None, f"Could not find pending account for {email}"

    approve = httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    assert approve.status_code == 200, f"Approve failed: {approve.text}"
    time.sleep(0.2)

    return _login(email, "parentpassword123")


@pytest.fixture(scope="module")
def admin_token() -> str:
    return _login(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="module")
def parent_token(admin_token: str) -> str:
    return _register_and_approve(admin_token)


@pytest.fixture(scope="module")
def second_parent_token(admin_token: str) -> str:
    return _register_and_approve(admin_token)


@pytest.mark.integration
def test_list_child_profiles_empty(parent_token: str) -> None:
    """Authenticated parent gets empty list when no profiles exist."""
    resp = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles",
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    )
    assert resp.status_code == 200
    assert resp.json()["profiles"] == []


@pytest.mark.integration
def test_create_child_profile(parent_token: str) -> None:
    """POST creates a profile; GET returns it."""
    resp = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles",
        json={"display_name": "Alice"},
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    )
    assert resp.status_code == 201
    assert resp.json()["display_name"] == "Alice"

    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles",
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    names = [p["display_name"] for p in list_resp.json()["profiles"]]
    assert "Alice" in names


@pytest.mark.integration
def test_create_profile_at_limit_returns_409(parent_token: str) -> None:
    """6th profile creation returns 409."""
    existing = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles",
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    ).json()["profiles"]

    for i in range(5 - len(existing)):
        r = httpx.post(
            f"{BASE_URL}/api/v1/child-profiles",
            json={"display_name": f"Extra{i}"},
            headers={"Authorization": f"Bearer {parent_token}"},
            timeout=10.0,
        )
        assert r.status_code == 201

    over = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles",
        json={"display_name": "TooMany"},
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    )
    assert over.status_code == 409


@pytest.mark.integration
def test_delete_other_accounts_profile_returns_403(
    parent_token: str, second_parent_token: str
) -> None:
    """Parent cannot delete another parent's child profile."""
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles",
        json={"display_name": "Victim"},
        headers={"Authorization": f"Bearer {second_parent_token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    resp = httpx.delete(
        f"{BASE_URL}/api/v1/child-profiles/{profile_id}",
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    )
    assert resp.status_code == 403


@pytest.mark.integration
def test_delete_own_profile(parent_token: str) -> None:
    """Parent can delete their own child profile and it disappears from the list."""
    with httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {parent_token}"},
        timeout=10.0,
    ) as client:
        created = client.post("/api/v1/child-profiles", json={"display_name": "ToDelete"})
        assert created.status_code == 201
        profile_id = created.json()["id"]

        resp = client.delete(f"/api/v1/child-profiles/{profile_id}")
        assert resp.status_code == 204

        listed = client.get("/api/v1/child-profiles")
        assert all(p["id"] != profile_id for p in listed.json()["profiles"])
