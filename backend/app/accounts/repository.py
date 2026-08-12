from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account, ApprovalStatus, RefreshToken


class AccountRepository(Protocol):
    async def get_by_id(self, account_id: uuid.UUID) -> Account | None: ...
    async def get_by_email(self, email: str) -> Account | None: ...
    async def save(self, account: Account) -> Account: ...
    async def list_by_status(
        self,
        status: str | None,
        role: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Account], int]: ...
    async def count_approved_administrators(self) -> int: ...


class RefreshTokenRepository(Protocol):
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None: ...
    async def save(self, token: RefreshToken) -> RefreshToken: ...
    async def revoke(
        self, token_id: uuid.UUID, replaced_by_id: uuid.UUID | None = None
    ) -> None: ...
    async def revoke_all_for_account(self, account_id: uuid.UUID) -> None: ...


class SQLAlchemyAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        result = await self._session.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Account | None:
        result = await self._session.execute(
            select(Account).where(Account.email == email)
        )
        return result.scalar_one_or_none()

    async def save(self, account: Account) -> Account:
        self._session.add(account)
        await self._session.flush()
        await self._session.refresh(account)
        return account

    async def list_by_status(
        self,
        status: str | None,
        role: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Account], int]:
        query = select(Account)
        count_query = select(func.count()).select_from(Account)

        if status is not None:
            query = query.where(Account.approval_status == status)
            count_query = count_query.where(Account.approval_status == status)
        if role is not None:
            query = query.where(Account.role == role)
            count_query = count_query.where(Account.role == role)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        accounts_result = await self._session.execute(
            query.order_by(Account.created_at.desc()).limit(limit).offset(offset)
        )
        return list(accounts_result.scalars().all()), total

    async def count_approved_administrators(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Account)
            .where(
                Account.role == "administrator",
                Account.approval_status == ApprovalStatus.approved,
            )
        )
        return result.scalar_one()


class SQLAlchemyRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def save(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        await self._session.flush()
        await self._session.refresh(token)
        return token

    async def revoke(
        self, token_id: uuid.UUID, replaced_by_id: uuid.UUID | None = None
    ) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(
                revoked_at=datetime.now(tz=UTC),
                replaced_by=replaced_by_id,
            )
        )

    async def revoke_all_for_account(self, account_id: uuid.UUID) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.account_id == account_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(tz=UTC))
        )
