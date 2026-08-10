"""Integration tests for GET /api/v1/opponents/personalities."""

from __future__ import annotations

import httpx
import os
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")

VALID_SPEED_PROFILES = {"uniform", "front_loaded", "back_loaded", "random"}


@pytest.mark.integration
def test_get_personalities_returns_200_without_auth() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/opponents/personalities", timeout=10.0)
    assert resp.status_code == 200, resp.text


@pytest.mark.integration
def test_get_personalities_returns_5_items() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/opponents/personalities", timeout=10.0)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5


@pytest.mark.integration
def test_get_personalities_items_have_required_fields() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/opponents/personalities", timeout=10.0)
    data = resp.json()
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "accuracyRate" in item
        assert "baseResponseTimeMs" in item
        assert "responseTimeVarianceMs" in item
        assert "speedProfile" in item
        assert "tierOffset" in item


@pytest.mark.integration
def test_get_personalities_speed_profiles_are_valid() -> None:
    resp = httpx.get(f"{BASE_URL}/api/v1/opponents/personalities", timeout=10.0)
    data = resp.json()
    for item in data:
        assert item["speedProfile"] in VALID_SPEED_PROFILES, (
            f"{item['id']} has invalid speedProfile: {item['speedProfile']}"
        )
