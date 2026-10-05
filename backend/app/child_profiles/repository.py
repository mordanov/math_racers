from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.child_profiles.models import ChildProfile


class ChildProfileRepository(Protocol):
    async def get(self, profile_id: uuid.UUID) -> ChildProfile | None: ...
    async def list_for_account(self, account_id: uuid.UUID) -> list[ChildProfile]: ...
    async def create(self, account_id: uuid.UUID, display_name: str) -> ChildProfile: ...
    async def delete(self, profile_id: uuid.UUID) -> None: ...
    async def count_for_account(self, account_id: uuid.UUID) -> int: ...


class SQLAlchemyChildProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, profile_id: uuid.UUID) -> ChildProfile | None:
        result = await self._session.execute(
            select(ChildProfile).where(ChildProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def list_for_account(self, account_id: uuid.UUID) -> list[ChildProfile]:
        result = await self._session.execute(
            select(ChildProfile)
            .where(ChildProfile.account_id == account_id)
            .order_by(ChildProfile.created_at)
        )
        return list(result.scalars().all())

    async def create(self, account_id: uuid.UUID, display_name: str) -> ChildProfile:
        profile = ChildProfile(account_id=account_id, display_name=display_name)
        self._session.add(profile)
        await self._session.flush()
        return profile

    async def delete(self, profile_id: uuid.UUID) -> None:
        profile = await self.get(profile_id)
        if profile is not None:
            await self._session.delete(profile)

    async def count_for_account(self, account_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(ChildProfile.account_id == account_id)
        )
        return result.scalar_one()
