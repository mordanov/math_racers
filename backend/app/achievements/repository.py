from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.achievements.models import PlayerAchievement


class AchievementRepository(Protocol):
    async def get_unlocked(self, account_id: uuid.UUID) -> list[PlayerAchievement]: ...

    async def unlock(
        self,
        account_id: uuid.UUID,
        achievement_key: str,
        avatar_id: uuid.UUID | None = None,
    ) -> PlayerAchievement | None: ...


class SQLAlchemyAchievementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_unlocked(self, account_id: uuid.UUID) -> list[PlayerAchievement]:
        from sqlalchemy import select

        result = await self._session.execute(
            select(PlayerAchievement).where(PlayerAchievement.account_id == account_id)
        )
        return list(result.scalars().all())

    async def unlock(
        self,
        account_id: uuid.UUID,
        achievement_key: str,
        avatar_id: uuid.UUID | None = None,
    ) -> PlayerAchievement | None:
        result = await self._session.execute(
            text("""
                INSERT INTO player_achievements (account_id, achievement_key, avatar_id)
                VALUES (:account_id, :achievement_key, :avatar_id)
                ON CONFLICT (account_id, achievement_key) DO NOTHING
                RETURNING id, account_id, achievement_key, avatar_id, unlocked_at
                """),
            {
                "account_id": str(account_id),
                "achievement_key": achievement_key,
                "avatar_id": str(avatar_id) if avatar_id else None,
            },
        )
        row = result.fetchone()
        if row is None:
            return None
        obj = PlayerAchievement()
        obj.id = row.id
        obj.account_id = row.account_id
        obj.achievement_key = row.achievement_key
        obj.avatar_id = row.avatar_id
        obj.unlocked_at = row.unlocked_at
        return obj
