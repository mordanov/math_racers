"""Integration tests for child profiles API endpoints.

Requires the full stack running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.database.engine import get_engine
from tests.integration import httpx_client as httpx

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
def test_delete_own_profile() -> None:
    """Parent can delete their own child profile and it disappears from the list."""
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    fresh_token = _register_and_approve(admin_token)
    with httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {fresh_token}"},
        timeout=10.0,
    ) as client:
        created = client.post("/api/v1/child-profiles", json={"display_name": "ToDelete"})
        assert created.status_code == 201
        profile_id = created.json()["id"]

        resp = client.delete(f"/api/v1/child-profiles/{profile_id}")
        assert resp.status_code == 204

        listed = client.get("/api/v1/child-profiles")
        assert all(p["id"] != profile_id for p in listed.json()["profiles"])


@pytest.mark.integration
def test_legacy_progression_assignment_export_and_child_deletion() -> None:
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    token = _register_and_approve(admin_token)
    headers = {"Authorization": f"Bearer {token}"}
    first = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles",
        json={"display_name": "First child"},
        headers=headers,
        timeout=10.0,
    )
    second = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles",
        json={"display_name": "Second child"},
        headers=headers,
        timeout=10.0,
    )
    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text
    first_id = first.json()["id"]
    second_id = second.json()["id"]
    account_id = uuid.UUID(first.json()["account_id"])
    second_profile_id = uuid.UUID(second_id)

    async def seed_progressions() -> None:
        async with async_sessionmaker(get_engine(), expire_on_commit=False)() as session:
            await session.execute(
                text("""
                    INSERT INTO player_progressions (account_id, total_xp, current_level)
                    VALUES (:account_id, 450, 2)
                    """),
                {"account_id": account_id},
            )
            await session.execute(
                text("""
                    INSERT INTO child_progressions
                        (child_profile_id, account_id, total_xp, current_level)
                    VALUES (:child_profile_id, :account_id, 75, 1)
                    """),
                {"child_profile_id": second_profile_id, "account_id": account_id},
            )
            await session.commit()

    asyncio.run(seed_progressions())

    legacy = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}/legacy-data",
        headers=headers,
        timeout=10.0,
    )
    assert legacy.status_code == 200, legacy.text
    progression = next(
        record for record in legacy.json()["records"] if record["record_type"] == "progression"
    )

    other_parent = _register_and_approve(admin_token)
    forbidden = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}/export",
        headers={"Authorization": f"Bearer {other_parent}"},
        timeout=10.0,
    )
    assert forbidden.status_code == 403, forbidden.text

    unassigned_export = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}/export",
        headers=headers,
        timeout=10.0,
    )
    assert unassigned_export.status_code == 200, unassigned_export.text
    assert unassigned_export.json()["progression"] == []

    assigned = httpx.post(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}/legacy-data/assign",
        json={"records": [{"record_type": "progression", "record_id": progression["record_id"]}]},
        headers=headers,
        timeout=10.0,
    )
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["assigned"] == 1

    first_export = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}/export",
        headers=headers,
        timeout=10.0,
    )
    second_export = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{second_id}/export",
        headers=headers,
        timeout=10.0,
    )
    assert first_export.status_code == 200, first_export.text
    assert second_export.status_code == 200, second_export.text
    assert [row["total_xp"] for row in first_export.json()["progression"]] == [450]
    assert [row["total_xp"] for row in second_export.json()["progression"]] == [75]

    deleted = httpx.delete(
        f"{BASE_URL}/api/v1/child-profiles/{first_id}",
        headers=headers,
        timeout=10.0,
    )
    assert deleted.status_code == 204, deleted.text
    remaining = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles",
        headers=headers,
        timeout=10.0,
    )
    assert [profile["id"] for profile in remaining.json()["profiles"]] == [second_id]
    second_export_after_delete = httpx.get(
        f"{BASE_URL}/api/v1/child-profiles/{second_id}/export",
        headers=headers,
        timeout=10.0,
    )
    assert second_export_after_delete.status_code == 200, second_export_after_delete.text
    assert [row["total_xp"] for row in second_export_after_delete.json()["progression"]] == [75]
