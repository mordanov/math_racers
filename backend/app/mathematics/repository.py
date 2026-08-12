from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mathematics.models import PlayerDifficulty


class PlayerDifficultyRepository(Protocol):
    async def get_by_player_id(self, player_id: uuid.UUID) -> PlayerDifficulty | None: ...
    async def upsert(self, record: PlayerDifficulty) -> PlayerDifficulty: ...


class SQLAlchemyPlayerDifficultyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_player_id(self, player_id: uuid.UUID) -> PlayerDifficulty | None:
        result = await self._session.execute(
            select(PlayerDifficulty).where(PlayerDifficulty.player_id == player_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, record: PlayerDifficulty) -> PlayerDifficulty:
        merged = await self._session.merge(record)
        await self._session.flush()
        await self._session.refresh(merged)
        return merged
