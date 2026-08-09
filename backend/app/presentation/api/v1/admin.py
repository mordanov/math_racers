from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.accounts.repository import SQLAlchemyAccountRepository
from app.accounts.schemas import AccountResponse
from application.approve_account import ApproveAccountUseCase
from application.list_accounts import ListAccountsUseCase
from application.reject_account import RejectAccountUseCase
from app.presentation.api.middleware.auth import require_administrator
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/accounts")
async def list_accounts(
    status: str | None = Query(None),
    role: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: Account = Depends(require_administrator),
    session: AsyncSession = Depends(get_session),
) -> dict:
    account_repo = SQLAlchemyAccountRepository(session)
    use_case = ListAccountsUseCase(account_repo)
    accounts, total = await use_case.execute(status, role, limit, offset)
    return {
        "items": [AccountResponse.model_validate(a).model_dump() for a in accounts],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/accounts/{account_id}/approve", response_model=AccountResponse)
async def approve_account(
    account_id: uuid.UUID,
    admin: Account = Depends(require_administrator),
    session: AsyncSession = Depends(get_session),
) -> AccountResponse:
    account_repo = SQLAlchemyAccountRepository(session)
    use_case = ApproveAccountUseCase(account_repo)
    updated = await use_case.execute(account_id, admin.id)
    return AccountResponse.model_validate(updated)


@router.post("/accounts/{account_id}/reject", response_model=AccountResponse)
async def reject_account(
    account_id: uuid.UUID,
    admin: Account = Depends(require_administrator),
    session: AsyncSession = Depends(get_session),
) -> AccountResponse:
    account_repo = SQLAlchemyAccountRepository(session)
    use_case = RejectAccountUseCase(account_repo)
    updated = await use_case.execute(account_id)
    return AccountResponse.model_validate(updated)
