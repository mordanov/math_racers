from __future__ import annotations

import uuid
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.championships.models import Championship, ChampionshipRace
from app.shared.exceptions import ConflictError, NotFoundError


class ChampionshipRepository(Protocol):
    async def create(self, account_id: uuid.UUID, total_races: int) -> Championship: ...
    async def get(self, championship_id: uuid.UUID) -> Championship: ...
    async def add_race(
        self,
        championship: Championship,
        race_id: uuid.UUID,
        race_index: int,
        participants: list[dict[str, Any]],
    ) -> Championship: ...


class SQLAlchemyChampionshipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, account_id: uuid.UUID, total_races: int) -> Championship:
        championship = Championship(account_id=account_id, total_races=total_races)
        self._session.add(championship)
        await self._session.flush()
        await self._session.refresh(championship)
        return championship

    async def get(self, championship_id: uuid.UUID) -> Championship:
        result = await self._session.execute(
            select(Championship)
            .where(Championship.id == championship_id)
            .options(selectinload(Championship.championship_races))
        )
        championship = result.scalar_one_or_none()
        if championship is None:
            raise NotFoundError(
                error_code="CHAMPIONSHIP_NOT_FOUND",
                message=f"Championship {championship_id} not found.",
            )
        return championship

    async def add_race(
        self,
        championship: Championship,
        race_id: uuid.UUID,
        race_index: int,
        participants: list[dict[str, Any]],
    ) -> Championship:
        existing_races = championship.championship_races
        if any(str(cr.race_id) == str(race_id) for cr in existing_races):
            raise ConflictError(
                error_code="RACE_ALREADY_RECORDED",
                message=f"Race {race_id} is already recorded for this championship.",
            )
        if any(cr.race_index == race_index for cr in existing_races):
            raise ConflictError(
                error_code="RACE_INDEX_ALREADY_RECORDED",
                message=f"Race index {race_index} is already recorded for this championship.",
            )

        for p in participants:
            row = ChampionshipRace(
                championship_id=championship.id,
                race_id=race_id,
                race_index=race_index,
                avatar_id=p["avatar_id"],
                is_player=p["is_player"],
                finishing_position=p["finishing_position"],
                points_earned=p["points_earned"],
            )
            self._session.add(row)

        championship.races_completed += 1
        if championship.races_completed >= championship.total_races:
            championship.status = "completed"

        await self._session.flush()
        await self._session.refresh(championship, ["championship_races"])
        return championship
