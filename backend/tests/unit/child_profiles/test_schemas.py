"""Unit tests for child profile Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.child_profiles.schemas import (
    ChildProfileListResponse,
    ChildProfileResponse,
    CreateChildProfileRequest,
)


def test_create_request_validates_max_length():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CreateChildProfileRequest(display_name="A" * 51)


def test_create_request_rejects_empty():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CreateChildProfileRequest(display_name="")


def test_child_profile_response_fields():
    r = ChildProfileResponse(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        display_name="Alice",
        created_at=datetime.now(UTC),
    )
    assert r.display_name == "Alice"


def test_child_profile_list_response():
    r = ChildProfileListResponse(profiles=[])
    assert r.profiles == []
