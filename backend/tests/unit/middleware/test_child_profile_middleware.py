"""Unit tests for child profile ownership middleware."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.child_profile import get_child_profile_dependency
from app.shared.exceptions import NotFoundError, PermissionError


def _make_account(role: str = "parent") -> Account:
    return Account(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="x",
        role=role,
        approval_status=ApprovalStatus.approved,
    )


def _make_profile(account_id: uuid.UUID) -> ChildProfile:
    return ChildProfile(id=uuid.uuid4(), account_id=account_id, display_name="Alice")


@pytest.mark.asyncio
async def test_parent_can_access_own_profile():
    account = _make_account("parent")
    profile = _make_profile(account.id)
    repo = AsyncMock()
    repo.get.return_value = profile

    result = await get_child_profile_dependency(profile.id, account, repo)
    assert result.id == profile.id


@pytest.mark.asyncio
async def test_parent_cannot_access_other_profile():
    account = _make_account("parent")
    other_profile = _make_profile(uuid.uuid4())
    repo = AsyncMock()
    repo.get.return_value = other_profile

    with pytest.raises(PermissionError):
        await get_child_profile_dependency(other_profile.id, account, repo)


@pytest.mark.asyncio
async def test_administrator_can_access_any_profile():
    admin = _make_account("administrator")
    profile = _make_profile(uuid.uuid4())
    repo = AsyncMock()
    repo.get.return_value = profile

    result = await get_child_profile_dependency(profile.id, admin, repo)
    assert result.id == profile.id


@pytest.mark.asyncio
async def test_profile_not_found_raises_not_found_error():
    account = _make_account("parent")
    repo = AsyncMock()
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        await get_child_profile_dependency(uuid.uuid4(), account, repo)
