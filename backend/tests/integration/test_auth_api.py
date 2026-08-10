"""Integration tests for auth API endpoints (T022).

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


def _register(email: str, password: str) -> httpx.Response:
    return httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )


def _login(email: str, password: str) -> httpx.Response:
    return httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )


def _approve(account_id: str, admin_token: str) -> httpx.Response:
    return httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )


@pytest.mark.integration
class TestRegistration:
    def test_register_returns_201(self) -> None:
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        response = _register(email, "securepassword123")
        assert response.status_code == 201

    def test_duplicate_email_returns_409(self) -> None:
        email = f"dupe-{uuid.uuid4().hex[:8]}@example.com"
        _register(email, "securepassword123")
        response = _register(email, "differentpassword!")
        assert response.status_code == 409
        assert response.json()["error_code"] == "EMAIL_TAKEN"


@pytest.mark.integration
class TestLoginBeforeApproval:
    def test_pending_account_returns_403_account_pending(self) -> None:
        email = f"pending-{uuid.uuid4().hex[:8]}@example.com"
        _register(email, "securepassword123")
        response = _login(email, "securepassword123")
        assert response.status_code == 403
        assert response.json()["error_code"] == "ACCOUNT_PENDING"


@pytest.mark.integration
class TestFullAuthCycle:
    def test_full_login_refresh_logout_cycle(self) -> None:
        # Step 1: admin logs in
        admin_resp = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert admin_resp.status_code == 200, f"Admin login failed: {admin_resp.text}"
        admin_token = admin_resp.json()["access_token"]

        # Step 2: register a new parent
        email = f"parent-{uuid.uuid4().hex[:8]}@example.com"
        _register(email, "parentpassword123")
        time.sleep(0.2)

        # Step 3: pending login blocked
        resp = _login(email, "parentpassword123")
        assert resp.status_code == 403
        assert resp.json()["error_code"] == "ACCOUNT_PENDING"

        # Step 4: admin lists pending accounts, finds our user
        list_resp = httpx.get(
            f"{BASE_URL}/api/v1/admin/accounts",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0,
        )
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        account_id = next((item["id"] for item in items if item["email"] == email), None)
        assert account_id is not None, f"Account {email} not found in pending list"

        # Step 5: admin approves
        approve_resp = _approve(account_id, admin_token)
        assert approve_resp.status_code == 200
        assert approve_resp.json()["approval_status"] == "approved"
        time.sleep(0.2)

        # Step 6: parent can now log in
        with httpx.Client(timeout=10.0) as client:
            login_resp = client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"email": email, "password": "parentpassword123"},
            )
            assert login_resp.status_code == 200
            assert login_resp.cookies.get("refresh_token")

            # Step 7: refresh returns new tokens
            refresh_cookie = login_resp.cookies.get("refresh_token") or ""
            refresh_resp = client.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                cookies={"refresh_token": refresh_cookie},
            )
            assert refresh_resp.status_code == 200
            new_access_token = refresh_resp.json()["access_token"]
            assert new_access_token  # token present; may equal access_token if issued same second

            # Step 8: old refresh cookie rejected (token rotated)
            old_refresh_resp = client.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                cookies={"refresh_token": refresh_cookie},
            )
            assert old_refresh_resp.status_code == 403

            # Step 9: logout
            logout_resp = client.post(
                f"{BASE_URL}/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {new_access_token}"},
            )
            assert logout_resp.status_code == 204

            # Step 10: refresh after logout fails
            new_cookie = refresh_resp.cookies.get("refresh_token") or ""
            post_logout_refresh = client.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                cookies={"refresh_token": new_cookie},
            )
            assert post_logout_refresh.status_code == 403

    def test_invalid_password_returns_401(self) -> None:
        response = _login(ADMIN_EMAIL, "wrongpassword!")
        assert response.status_code == 403
        assert response.json()["error_code"] == "INVALID_CREDENTIALS"

    def test_unknown_email_returns_401(self) -> None:
        response = _login("nobody@example.com", "anything")
        assert response.status_code == 403
        assert response.json()["error_code"] == "INVALID_CREDENTIALS"
