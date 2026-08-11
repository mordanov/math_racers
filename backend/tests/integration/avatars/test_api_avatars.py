"""Integration tests for avatar endpoints.

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

pytestmark = pytest.mark.integration

_CREATE_BODY = {
    "species": "fox",
    "fur_color": "#FF6600",
    "eye_color": "#00AAFF",
    "hairstyle": "spiky",
    "accessories": ["glasses"],
    "clothes_top_color": "#4169E1",
    "clothes_bottom_color": "#FFFFFF",
}


def _login(email: str, password: str) -> str:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return str(resp.json()["access_token"])


def _register_and_approve() -> str:
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    email = f"avatar-integ-{uuid.uuid4().hex[:8]}@example.com"
    password = "password123!"

    reg = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert reg.status_code == 201

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
    assert account_id is not None

    httpx.post(
        f"{BASE_URL}/api/v1/admin/accounts/{account_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10.0,
    )
    time.sleep(0.2)
    return _login(email, password)


# ── Scenario 1: Create avatar ──────────────────────────────────────────────────


def test_create_avatar_returns_201() -> None:
    token = _register_and_approve()
    resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "avatar_id" in data
    assert "job_id" in data
    assert data["status"] == "queued"


# ── Scenario 2: Poll job status ────────────────────────────────────────────────


def test_poll_job_status() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    avatar_id = create_resp.json()["avatar_id"]
    job_id = create_resp.json()["job_id"]

    job_resp = httpx.get(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert job_resp.status_code == 200
    data = job_resp.json()
    assert data["job_id"] == job_id
    assert data["avatar_id"] == avatar_id
    assert data["status"] in (
        "queued",
        "llm_running",
        "prompt_building",
        "generating",
        "validating",
        "storing",
        "complete",
        "failed",
    )


# ── Scenario 4: List avatars ───────────────────────────────────────────────────


def test_list_avatars_includes_created() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    avatar_id = create_resp.json()["avatar_id"]

    list_resp = httpx.get(
        f"{BASE_URL}/api/v1/avatars",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert list_resp.status_code == 200
    ids = [a["avatar_id"] for a in list_resp.json()]
    assert avatar_id in ids


# ── Scenario 5: Get avatar detail ─────────────────────────────────────────────


def test_get_avatar_detail() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    avatar_id = create_resp.json()["avatar_id"]

    detail_resp = httpx.get(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert data["avatar_id"] == avatar_id
    assert data["species"] == "fox"
    assert data["fur_color"] == "#FF6600"


# ── Scenario 6: Avatar not found ──────────────────────────────────────────────


def test_get_nonexistent_avatar_returns_404() -> None:
    token = _register_and_approve()
    fake_id = str(uuid.uuid4())

    resp = httpx.get(
        f"{BASE_URL}/api/v1/avatars/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 404
    assert resp.json()["error_code"] == "AVATAR_NOT_FOUND"


# ── Scenario 10: Validation error ─────────────────────────────────────────────


def test_create_avatar_invalid_species_returns_422() -> None:
    token = _register_and_approve()
    body = {**_CREATE_BODY, "species": "dragon"}
    resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 422


def test_create_avatar_invalid_hex_color_returns_422() -> None:
    token = _register_and_approve()
    body = {**_CREATE_BODY, "fur_color": "orange"}
    resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert resp.status_code == 422


# ── Scenario 3: Regenerate portrait ───────────────────────────────────────────


def test_regenerate_portrait() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    avatar_id = create_resp.json()["avatar_id"]

    regen_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}/regenerate",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    # Will succeed (queued) or fail with CONCURRENCY_LIMIT_REACHED / RATE_LIMIT_EXCEEDED
    assert regen_resp.status_code in (201, 422)


# ── Scenario 7: Patch avatar ───────────────────────────────────────────────────


def test_patch_avatar_name() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201
    avatar_id = create_resp.json()["avatar_id"]

    patch_resp = httpx.patch(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}",
        json={"name": "Speedy Fox"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Speedy Fox"


# ── Scenario 8: Delete avatar ──────────────────────────────────────────────────


def test_delete_avatar() -> None:
    token = _register_and_approve()
    create_resp = httpx.post(
        f"{BASE_URL}/api/v1/avatars",
        json=_CREATE_BODY,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert create_resp.status_code == 201, create_resp.text
    avatar_id = create_resp.json()["avatar_id"]

    del_resp = httpx.delete(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert del_resp.status_code == 204, del_resp.text

    get_resp = httpx.get(
        f"{BASE_URL}/api/v1/avatars/{avatar_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert get_resp.status_code == 404
