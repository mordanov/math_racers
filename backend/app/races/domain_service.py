from __future__ import annotations

from typing import TYPE_CHECKING

from app.shared.exceptions import ValidationError

if TYPE_CHECKING:
    from app.races.repository import RaceRepository
    from app.races.schemas import RaceSummaryRequest, RaceSummaryResponse


class RaceDomainService:
    def __init__(self, repository: RaceRepository) -> None:
        self._repository = repository

    async def persist_race(self, request: RaceSummaryRequest) -> RaceSummaryResponse:
        positions = [p.position for p in request.participants]
        if len(positions) != len(set(positions)):
            raise ValidationError(message="Participant positions must be unique within a race.")

        return await self._repository.create(request)
