from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.races.models import Race, RaceParticipant
from app.races.schemas import RaceSummaryRequest, RaceSummaryResponse
from app.shared.exceptions import ConflictError


class RaceRepository(Protocol):
    async def create(self, request: RaceSummaryRequest) -> RaceSummaryResponse: ...


class SQLAlchemyRaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, request: RaceSummaryRequest) -> RaceSummaryResponse:
        existing = await self._session.execute(select(Race).where(Race.id == request.race_id))
        if existing.scalar_one_or_none() is not None:
            raise ConflictError(
                error_code="RACE_ALREADY_EXISTS",
                message=f"Race {request.race_id} already exists.",
            )

        race = Race(
            id=request.race_id,
            seed=request.seed,
            difficulty_tier=request.difficulty_tier,
            mode=request.mode,
            started_at=request.started_at,
            completed_at=request.completed_at,
        )
        self._session.add(race)
        await self._session.flush()

        for p in request.participants:
            participant = RaceParticipant(
                race_id=race.id,
                avatar_id=p.avatar_id,
                position=p.position,
                problems_correct=p.problems_correct,
                average_response_ms=p.average_response_ms,
                total_distance=p.total_distance,
                xp_earned=p.xp_earned,
            )
            self._session.add(participant)

        await self._session.flush()
        await self._session.refresh(race)

        return RaceSummaryResponse(race_id=race.id, created_at=race.created_at)
