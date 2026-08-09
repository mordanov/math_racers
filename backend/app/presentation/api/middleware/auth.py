from __future__ import annotations

import uuid

from fastapi import Depends, Request

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import Account, ApprovalStatus
from app.accounts.repository import AccountRepository, SQLAlchemyAccountRepository
from app.shared.exceptions import PermissionError
from infrastructure.config import Config, get_config
from infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession


async def get_account_repository(
    session: AsyncSession = Depends(get_session),
) -> AccountRepository:
    return SQLAlchemyAccountRepository(session)


async def get_current_account(
    request: Request,
    settings: Config = Depends(get_config),
    account_repo: AccountRepository = Depends(get_account_repository),
) -> Account:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise PermissionError("UNAUTHORIZED", "Authentication required.")

    token = auth_header.removeprefix("Bearer ").strip()
    domain_service = AccountDomainService()
    payload = domain_service.decode_access_token(token, settings)

    account_id = uuid.UUID(payload["sub"])
    account = await account_repo.get_by_id(account_id)
    if account is None:
        raise PermissionError("UNAUTHORIZED", "Account not found.")

    if account.approval_status != ApprovalStatus.approved:
        raise PermissionError("UNAUTHORIZED", "Account is not approved.")

    return account


async def require_administrator(
    account: Account = Depends(get_current_account),
) -> Account:
    if account.role != "administrator":
        raise PermissionError("FORBIDDEN", "Administrator access required.")
    return account
