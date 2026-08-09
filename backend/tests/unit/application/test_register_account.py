"""Unit tests for RegisterAccountUseCase (T020)."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.accounts.domain_service import AccountDomainService
from app.shared.exceptions import ConflictError
from application.register_account import RegisterAccountUseCase


def _make_account(**kwargs) -> Account:
    defaults = dict(
        id=uuid.uuid4(),
        email="user@example.com",
        password_hash="$2b$12$hashed",
        role=AccountRole.parent,
        approval_status=ApprovalStatus.pending,
    )
    defaults.update(kwargs)
    return Account(**defaults)


@pytest.fixture
def account_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_email.return_value = None
    repo.save.side_effect = lambda a: a
    return repo


@pytest.fixture
def domain_service() -> AccountDomainService:
    return AccountDomainService()


@pytest.fixture
def use_case(account_repo, domain_service) -> RegisterAccountUseCase:
    return RegisterAccountUseCase(account_repo, domain_service)


class TestRegisterAccount:
    async def test_happy_path_creates_pending_account(
        self, use_case: RegisterAccountUseCase, account_repo: AsyncMock
    ) -> None:
        await use_case.execute("User@Example.COM", "securepassword123")
        account_repo.save.assert_awaited_once()
        saved: Account = account_repo.save.call_args.args[0]
        assert saved.email == "user@example.com"
        assert saved.role == AccountRole.parent
        assert saved.approval_status == ApprovalStatus.pending

    async def test_duplicate_email_raises_conflict_error(
        self, use_case: RegisterAccountUseCase, account_repo: AsyncMock
    ) -> None:
        account_repo.get_by_email.return_value = _make_account()
        with pytest.raises(ConflictError) as exc_info:
            await use_case.execute("user@example.com", "securepassword123")
        assert exc_info.value.error_code == "EMAIL_TAKEN"

    async def test_email_is_normalised_to_lowercase(
        self, use_case: RegisterAccountUseCase, account_repo: AsyncMock
    ) -> None:
        await use_case.execute("  UPPER@EXAMPLE.COM  ", "securepassword123")
        account_repo.get_by_email.assert_awaited_with("upper@example.com")
        saved: Account = account_repo.save.call_args.args[0]
        assert saved.email == "upper@example.com"

    async def test_password_is_hashed_not_stored_plain(
        self, use_case: RegisterAccountUseCase, account_repo: AsyncMock
    ) -> None:
        plain = "securepassword123"
        await use_case.execute("user@example.com", plain)
        saved: Account = account_repo.save.call_args.args[0]
        assert saved.password_hash != plain
        assert saved.password_hash.startswith("$2b$")
