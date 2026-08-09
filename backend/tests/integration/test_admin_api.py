"""Integration tests for admin API endpoints (T029).

Requires the full stack running (docker compose up).
Run with: pytest -m integration
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword123")


def _login(email: str, password: str) -> httpx.Response:
    return httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )


def _admin_token() -> str:
    resp = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _register_and_get_id(email: str, admin_token: str) -> str:
    httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": "testpassword123"},
        timeout=10.0,
    )
    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/admin/accounts",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    items = list_resp.json()["items"]
    account_id = next((item["id"] for item in items if item["email"] == email), None)
    assert account_id is not None
    return str(account_id)


@pytest.mark.integration
class TestListAccounts:
    def test_admin_can_list_accounts(self) -> None:
        token = _admin_token()
        response = httpx.get(
            f"{BASE_URL}/api/v1/admin/accounts",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body

    def test_non_admin_gets_403(self) -> None:
        email = f"parent-{uuid.uuid4().hex[:8]}@example.com"
        token_admin = _admin_token()

        httpx.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={"email": email, "password": "testpassword123"},
            timeout=10.0,
        )
        account_id = _register_and_get_id(email, token_admin)
        httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
            headers={"Authorization": f"Bearer {token_admin}"},
            timeout=10.0,
        )

        parent_resp = _login(email, "testpassword123")
        parent_token = parent_resp.json()["access_token"]

        response = httpx.get(
            f"{BASE_URL}/api/v1/admin/accounts",
            headers={"Authorization": f"Bearer {parent_token}"},
            timeout=10.0,
        )
        assert response.status_code == 403

    def test_unauthenticated_gets_403(self) -> None:
        response = httpx.get(f"{BASE_URL}/api/v1/admin/accounts", timeout=10.0)
        assert response.status_code == 403

    def test_filter_by_status(self) -> None:
        token = _admin_token()
        response = httpx.get(
            f"{BASE_URL}/api/v1/admin/accounts",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert item["approval_status"] == "pending"


@pytest.mark.integration
class TestApproveAccount:
    def test_approve_pending_returns_200(self) -> None:
        token = _admin_token()
        email = f"approve-{uuid.uuid4().hex[:8]}@example.com"
        account_id = _register_and_get_id(email, token)

        response = httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert response.status_code == 200
        assert response.json()["approval_status"] == "approved"

    def test_approve_again_returns_400(self) -> None:
        token = _admin_token()
        email = f"approve2x-{uuid.uuid4().hex[:8]}@example.com"
        account_id = _register_and_get_id(email, token)

        httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        response = httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "INVALID_ACCOUNT_STATE"


@pytest.mark.integration
class TestRejectAccount:
    def test_reject_pending_returns_200(self) -> None:
        token = _admin_token()
        email = f"reject-{uuid.uuid4().hex[:8]}@example.com"
        account_id = _register_and_get_id(email, token)

        response = httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/reject",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        assert response.status_code == 200
        assert response.json()["approval_status"] == "rejected"

    def test_rejected_login_returns_403_account_rejected(self) -> None:
        token = _admin_token()
        email = f"rejected-{uuid.uuid4().hex[:8]}@example.com"
        account_id = _register_and_get_id(email, token)

        httpx.post(
            f"{BASE_URL}/api/v1/admin/accounts/{account_id}/reject",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )

        login_resp = httpx.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": "testpassword123"},
            timeout=10.0,
        )
        assert login_resp.status_code == 403
        assert login_resp.json()["error_code"] == "ACCOUNT_REJECTED"
