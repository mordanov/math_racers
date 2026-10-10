from __future__ import annotations

import uuid
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.championships.models import Championship, ChampionshipRace
from app.races.models import Race
from app.shared.exceptions import ConflictError, NotFoundError


class ChampionshipRepository(Protocol):
    async def create(
        self,
        account_id: uuid.UUID,
        total_races: int,
        child_profile_id: uuid.UUID | None = None,
    ) -> Championship: ...
    async def get(
        self, championship_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> Championship: ...
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

    async def create(
        self,
        account_id: uuid.UUID,
        total_races: int,
        child_profile_id: uuid.UUID | None = None,
    ) -> Championship:
        championship = Championship(
            account_id=account_id,
            child_profile_id=child_profile_id,
            total_races=total_races,
        )
        self._session.add(championship)
        await self._session.flush()
        return await self.get(championship.id, child_profile_id)

    async def get(
        self, championship_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> Championship:
        result = await self._session.execute(
            select(Championship)
            .where(
                Championship.id == championship_id,
                Championship.child_profile_id == child_profile_id,
            )
            .options(selectinload(Championship.championship_races))
            .with_for_update()
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
        race_result = await self._session.execute(
            select(Race)
            .where(
                Race.id == race_id,
                Race.account_id == championship.account_id,
                Race.child_profile_id == championship.child_profile_id,
                Race.championship_id == championship.id,
                Race.status == "completed",
            )
            .options(selectinload(Race.participants))
        )
        race = race_result.scalar_one_or_none()
        if race is None:
            raise ConflictError(
                error_code="RACE_NOT_IN_CHAMPIONSHIP",
                message="The completed race does not belong to this championship.",
            )

        persisted_results = {
            participant.avatar_id: participant.position for participant in race.participants
        }
        submitted_results = {participant["avatar_id"]: participant for participant in participants}
        if (
            len(submitted_results) != len(participants)
            or submitted_results.keys() != persisted_results.keys()
            or any(
                submitted_results[avatar_id]["finishing_position"] != position
                or submitted_results[avatar_id]["is_player"] != (avatar_id == race.avatar_id)
                for avatar_id, position in persisted_results.items()
            )
        ):
            raise ConflictError(
                error_code="CHAMPIONSHIP_RESULT_MISMATCH",
                message="Championship placements must match the saved race result.",
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
            championship.championship_races.append(row)

        championship.races_completed += 1
        if championship.races_completed >= championship.total_races:
            championship.status = "completed"

        await self._session.flush()
        return championship
