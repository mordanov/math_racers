from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.shared.exceptions import ValidationError

if TYPE_CHECKING:
    from app.progression.repository import ProgressionRepository
    from app.races.repository import RaceRepository
    from app.races.schemas import RaceSummaryRequest, RaceSummaryResponse


class RaceDomainService:
    def __init__(
        self,
        repository: RaceRepository,
        progression_repository: ProgressionRepository | None = None,
    ) -> None:
        self._repository = repository
        self._progression_repository = progression_repository

    async def persist_race(
        self,
        request: RaceSummaryRequest,
        account_id: uuid.UUID | None = None,
    ) -> RaceSummaryResponse:
        positions = [p.position for p in request.participants]
        if len(positions) != len(set(positions)):
            raise ValidationError(message="Participant positions must be unique within a race.")

        response = await self._repository.create(request)

        if account_id is not None and self._progression_repository is not None:
            from app.progression.domain_service import ProgressionDomainService

            player = next(
                (p for p in request.participants if p.position == 1),
                request.participants[0],
            )
            prog_service = ProgressionDomainService(self._progression_repository)
            response.progression = await prog_service.award_xp(
                account_id=account_id,
                problems_correct=player.problems_correct,
                longest_streak=player.longest_streak,
                mode=request.mode,
                race_id=request.race_id,
            )

        return response
