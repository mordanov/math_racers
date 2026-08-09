"""Unit tests for LoginUseCase (T021)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.shared.exceptions import PermissionError
from application.login import LoginUseCase
from infrastructure.config import Config


def _make_config() -> Config:
    return Config.model_validate(
        {
            "DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
            "REDIS_URL": "redis://localhost:6379/0",
            "JWT_SECRET": "test-secret-that-is-long-enough-32chars",
            "OPENAI_API_KEY": "sk-test",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "minio",
            "STORAGE_SECRET_KEY": "minio123",
            "STORAGE_BUCKET": "test",
            "ADMIN_EMAIL": "admin@example.com",
            "ADMIN_PASSWORD": "adminpass123",
        }
    )


def _make_account(
    status: str = ApprovalStatus.approved, plain_password: str = "correct"
) -> Account:
    svc = AccountDomainService()
    return Account(
        id=uuid.uuid4(),
        email="user@example.com",
        password_hash=svc.hash_password(plain_password),
        role=AccountRole.parent,
        approval_status=status,
        created_at=datetime.now(tz=UTC),
    )


@pytest.fixture
def cfg() -> Config:
    return _make_config()


@pytest.fixture
def account_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def refresh_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.save.side_effect = lambda t: t
    return repo


@pytest.fixture
def domain_service() -> AccountDomainService:
    return AccountDomainService()


@pytest.fixture
def use_case(
    account_repo: AsyncMock,
    refresh_repo: AsyncMock,
    domain_service: AccountDomainService,
) -> LoginUseCase:
    return LoginUseCase(account_repo, refresh_repo, domain_service)


@pytest.mark.unit
class TestLoginUseCase:
    async def test_approved_account_returns_tokens(
        self,
        use_case: LoginUseCase,
        account_repo: AsyncMock,
        cfg: Config,
    ) -> None:
        account_repo.get_by_email.return_value = _make_account()
        access_token, raw_refresh = await use_case.execute("user@example.com", "correct", cfg)
        assert access_token
        assert raw_refresh

    async def test_pending_account_raises_account_pending(
        self,
        use_case: LoginUseCase,
        account_repo: AsyncMock,
        cfg: Config,
    ) -> None:
        account_repo.get_by_email.return_value = _make_account(ApprovalStatus.pending)
        with pytest.raises(PermissionError) as exc_info:
            await use_case.execute("user@example.com", "correct", cfg)
        assert exc_info.value.error_code == "ACCOUNT_PENDING"

    async def test_rejected_account_raises_account_rejected(
        self,
        use_case: LoginUseCase,
        account_repo: AsyncMock,
        cfg: Config,
    ) -> None:
        account_repo.get_by_email.return_value = _make_account(ApprovalStatus.rejected)
        with pytest.raises(PermissionError) as exc_info:
            await use_case.execute("user@example.com", "correct", cfg)
        assert exc_info.value.error_code == "ACCOUNT_REJECTED"

    async def test_wrong_password_raises_invalid_credentials(
        self,
        use_case: LoginUseCase,
        account_repo: AsyncMock,
        cfg: Config,
    ) -> None:
        account_repo.get_by_email.return_value = _make_account()
        with pytest.raises(PermissionError) as exc_info:
            await use_case.execute("user@example.com", "wrong", cfg)
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"

    async def test_unknown_email_raises_invalid_credentials(
        self,
        use_case: LoginUseCase,
        account_repo: AsyncMock,
        cfg: Config,
    ) -> None:
        account_repo.get_by_email.return_value = None
        with pytest.raises(PermissionError) as exc_info:
            await use_case.execute("nobody@example.com", "anything", cfg)
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
