from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.progression.models import PlayerProgression, XPEvent


class ProgressionRepository(Protocol):
    async def get(self, account_id: uuid.UUID) -> PlayerProgression | None: ...

    async def upsert(
        self,
        account_id: uuid.UUID,
        new_total: int,
        new_level: int,
    ) -> PlayerProgression: ...

    async def insert_event(
        self,
        account_id: uuid.UUID,
        source: str,
        amount: int,
        race_id: uuid.UUID | None,
    ) -> None: ...


class SQLAlchemyProgressionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, account_id: uuid.UUID) -> PlayerProgression | None:
        from sqlalchemy import select

        result = await self._session.execute(
            select(PlayerProgression).where(PlayerProgression.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        account_id: uuid.UUID,
        new_total: int,
        new_level: int,
    ) -> PlayerProgression:
        await self._session.execute(
            text("""
                INSERT INTO player_progressions (account_id, total_xp, current_level, updated_at)
                VALUES (:account_id, :total_xp, :current_level, now())
                ON CONFLICT (account_id) DO UPDATE
                SET total_xp = :total_xp,
                    current_level = :current_level,
                    updated_at = now()
                """),
            {
                "account_id": str(account_id),
                "total_xp": new_total,
                "current_level": new_level,
            },
        )
        row = await self.get(account_id)
        assert row is not None
        return row

    async def insert_event(
        self,
        account_id: uuid.UUID,
        source: str,
        amount: int,
        race_id: uuid.UUID | None,
    ) -> None:
        event = XPEvent(
            account_id=account_id,
            source=source,
            amount=amount,
            race_id=race_id,
        )
        self._session.add(event)
        await self._session.flush()
