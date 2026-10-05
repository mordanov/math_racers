"""Unit tests for ChildProfileRepository protocol."""

from __future__ import annotations

from app.child_profiles.repository import ChildProfileRepository, SQLAlchemyChildProfileRepository


def test_repository_protocol_methods() -> None:
    """Protocol has all required method names."""
    for name in ("get", "list_for_account", "create", "delete", "count_for_account"):
        assert hasattr(ChildProfileRepository, name), f"missing method: {name}"


def test_sqlalchemy_repository_implements_protocol() -> None:
    """SQLAlchemyChildProfileRepository has the required interface."""
    for name in ("get", "list_for_account", "create", "delete", "count_for_account"):
        assert hasattr(SQLAlchemyChildProfileRepository, name), f"missing method: {name}"
