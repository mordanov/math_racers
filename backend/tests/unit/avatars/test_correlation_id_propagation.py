"""Unit tests — request_id propagation through _enqueue_job."""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.logging import request_id_var


@pytest.mark.unit
def test_enqueue_job_includes_request_id_from_context_var() -> None:
    """_enqueue_job embeds the active request_id in the Redis payload."""
    from app.avatars.domain_service import _enqueue_job

    expected_rid = str(uuid.uuid4())
    token = request_id_var.set(expected_rid)

    captured: list[str] = []
    mock_client = MagicMock()
    mock_client.rpush.side_effect = lambda _key, payload: captured.append(str(payload))

    with patch("redis.from_url", return_value=mock_client):
        _enqueue_job("redis://localhost", uuid.uuid4(), uuid.uuid4())

    request_id_var.reset(token)

    assert len(captured) == 1
    data = json.loads(captured[0])
    assert data["request_id"] == expected_rid


@pytest.mark.unit
def test_enqueue_job_uses_nil_uuid_when_no_request_context() -> None:
    """_enqueue_job uses the nil UUID when no request context is active."""
    from app.avatars.domain_service import _enqueue_job

    captured: list[str] = []
    mock_client = MagicMock()
    mock_client.rpush.side_effect = lambda _key, payload: captured.append(str(payload))

    with patch("redis.from_url", return_value=mock_client):
        _enqueue_job("redis://localhost", uuid.uuid4(), uuid.uuid4())

    data = json.loads(captured[0])
    assert data["request_id"] == "00000000-0000-0000-0000-000000000000"
