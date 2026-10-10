from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.progression.models import ChildProgression, PlayerProgression, XPEvent


class ProgressionRepository(Protocol):
    async def get(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> PlayerProgression | ChildProgression | None: ...

    async def add_xp(
        self,
        account_id: uuid.UUID,
        amount: int,
        child_profile_id: uuid.UUID | None = None,
    ) -> tuple[int, int]: ...

    async def insert_event(
        self,
        account_id: uuid.UUID,
        source: str,
        amount: int,
        race_id: uuid.UUID | None,
        child_profile_id: uuid.UUID | None = None,
    ) -> None: ...

    async def insert_championship_bonus_event(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        championship_id: uuid.UUID,
    ) -> bool: ...


class SQLAlchemyProgressionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> PlayerProgression | ChildProgression | None:
        from sqlalchemy import select

        if child_profile_id is not None:
            result = await self._session.execute(
                select(ChildProgression).where(
                    ChildProgression.account_id == account_id,
                    ChildProgression.child_profile_id == child_profile_id,
                )
            )
            return result.scalar_one_or_none()
        result = await self._session.execute(
            select(PlayerProgression).where(PlayerProgression.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def add_xp(
        self,
        account_id: uuid.UUID,
        amount: int,
        child_profile_id: uuid.UUID | None = None,
    ) -> tuple[int, int]:
        if child_profile_id is not None:
            result = await self._session.execute(
                text("""
                    INSERT INTO child_progressions
                        (child_profile_id, account_id, total_xp, current_level, updated_at)
                    VALUES
                        (
                            :child_profile_id,
                            :account_id,
                            :amount,
                            GREATEST(
                                1,
                                FLOOR(SQRT(CAST(:amount_for_level AS numeric) / 100))
                            )::integer,
                            now()
                        )
                    ON CONFLICT (child_profile_id) DO UPDATE
                    SET total_xp = child_progressions.total_xp + EXCLUDED.total_xp,
                        current_level = GREATEST(
                            1,
                            FLOOR(SQRT(
                                (child_progressions.total_xp + EXCLUDED.total_xp)::numeric / 100
                            ))
                        )::integer,
                        updated_at = now()
                    RETURNING total_xp, current_level
                    """),
                {
                    "child_profile_id": str(child_profile_id),
                    "account_id": str(account_id),
                    "amount": amount,
                    "amount_for_level": amount,
                },
            )
            row = result.one()
            return int(row.total_xp), int(row.current_level)
        result = await self._session.execute(
            text("""
                INSERT INTO player_progressions (account_id, total_xp, current_level, updated_at)
                VALUES (
                    :account_id,
                    :amount,
                    GREATEST(
                        1,
                        FLOOR(SQRT(CAST(:amount_for_level AS numeric) / 100))
                    )::integer,
                    now()
                )
                ON CONFLICT (account_id) DO UPDATE
                SET total_xp = player_progressions.total_xp + EXCLUDED.total_xp,
                    current_level = GREATEST(
                        1,
                        FLOOR(SQRT(
                            (player_progressions.total_xp + EXCLUDED.total_xp)::numeric / 100
                        ))
                    )::integer,
                    updated_at = now()
                RETURNING total_xp, current_level
                """),
            {
                "account_id": str(account_id),
                "amount": amount,
                "amount_for_level": amount,
            },
        )
        row = result.one()
        return int(row.total_xp), int(row.current_level)

    async def insert_event(
        self,
        account_id: uuid.UUID,
        source: str,
        amount: int,
        race_id: uuid.UUID | None,
        child_profile_id: uuid.UUID | None = None,
    ) -> None:
        event = XPEvent(
            account_id=account_id,
            source=source,
            amount=amount,
            race_id=race_id,
            child_profile_id=child_profile_id,
        )
        self._session.add(event)
        await self._session.flush()

    async def insert_championship_bonus_event(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        championship_id: uuid.UUID,
    ) -> bool:
        result = await self._session.execute(
            text("""
                INSERT INTO xp_events
                    (account_id, child_profile_id, source, amount, championship_id)
                VALUES
                    (:account_id, :child_profile_id, 'championship_bonus', 500, :championship_id)
                ON CONFLICT (championship_id)
                    WHERE source = 'championship_bonus' AND championship_id IS NOT NULL
                DO NOTHING
                RETURNING id
                """),
            {
                "account_id": str(account_id),
                "child_profile_id": str(child_profile_id),
                "championship_id": str(championship_id),
            },
        )
        return result.scalar_one_or_none() is not None
