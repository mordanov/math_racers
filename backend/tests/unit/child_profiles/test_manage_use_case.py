from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.shared.exceptions import ConflictError, NotFoundError, PermissionError
from application.manage_child_profiles import ManageChildProfilesUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_rejects_profile_count_above_limit() -> None:
    repository = MagicMock()
    repository.count_for_account = AsyncMock(return_value=5)
    repository.create = AsyncMock()
    service = ManageChildProfilesUseCase(repository)

    with pytest.raises(ConflictError, match="Maximum of 5"):
        await service.create(uuid.uuid4(), "Sixth child")

    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_owned_rejects_missing_or_foreign_profiles() -> None:
    account_id = uuid.uuid4()
    repository = MagicMock()
    repository.get = AsyncMock(return_value=None)
    service = ManageChildProfilesUseCase(repository)

    with pytest.raises(NotFoundError):
        await service.get_owned(account_id, uuid.uuid4())

    repository.get.return_value = SimpleNamespace(account_id=uuid.uuid4())
    with pytest.raises(PermissionError):
        await service.get_owned(account_id, uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_checks_ownership_before_deleting_profile() -> None:
    account_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    repository = MagicMock()
    repository.get = AsyncMock(return_value=SimpleNamespace(account_id=account_id))
    repository.delete = AsyncMock()

    await ManageChildProfilesUseCase(repository).delete(account_id, profile_id)

    repository.delete.assert_awaited_once_with(profile_id)
