"""Unit tests for ChildProfile ORM model."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.child_profiles.models import ChildProfile


def test_child_profile_model_has_required_fields():
    profile = ChildProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        display_name="Alice",
        created_at=datetime.now(UTC),
    )
    assert profile.display_name == "Alice"
    assert profile.__tablename__ == "child_profiles"
