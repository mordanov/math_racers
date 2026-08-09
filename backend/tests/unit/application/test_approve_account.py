"""Unit tests for ApproveAccountUseCase (T028)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.shared.exceptions import NotFoundError, ValidationError
from application.approve_account import ApproveAccountUseCase


def _make_account(status: str = ApprovalStatus.pending) -> Account:
    return Account(
        id=uuid.uuid4(),
        email="user@example.com",
        password_hash="$2b$12$hashed",
        role=AccountRole.parent,
        approval_status=status,
        created_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture
def account_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda a: a
    return repo


@pytest.fixture
def use_case(account_repo) -> ApproveAccountUseCase:
    return ApproveAccountUseCase(account_repo)


class TestApproveAccount:
    async def test_happy_path_sets_approved_fields(
        self, use_case: ApproveAccountUseCase, account_repo: AsyncMock
    ) -> None:
        target = _make_account(ApprovalStatus.pending)
        admin_id = uuid.uuid4()
        account_repo.get_by_id.return_value = target

        result = await use_case.execute(target.id, admin_id)

        assert result.approval_status == ApprovalStatus.approved
        assert result.approved_by == admin_id
        assert result.approved_at is not None

    async def test_already_approved_raises_invalid_account_state(
        self, use_case: ApproveAccountUseCase, account_repo: AsyncMock
    ) -> None:
        target = _make_account(ApprovalStatus.approved)
        account_repo.get_by_id.return_value = target

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(target.id, uuid.uuid4())
        assert exc_info.value.error_code == "INVALID_ACCOUNT_STATE"

    async def test_rejected_account_raises_invalid_account_state(
        self, use_case: ApproveAccountUseCase, account_repo: AsyncMock
    ) -> None:
        target = _make_account(ApprovalStatus.rejected)
        account_repo.get_by_id.return_value = target

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(target.id, uuid.uuid4())
        assert exc_info.value.error_code == "INVALID_ACCOUNT_STATE"

    async def test_not_found_raises_not_found_error(
        self, use_case: ApproveAccountUseCase, account_repo: AsyncMock
    ) -> None:
        account_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await use_case.execute(uuid.uuid4(), uuid.uuid4())
        assert exc_info.value.error_code == "ACCOUNT_NOT_FOUND"
