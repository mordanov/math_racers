from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.shared.exceptions import ValidationError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.achievements.repository import AchievementRepository
    from app.progression.repository import ProgressionRepository
    from app.races.repository import RaceRepository
    from app.races.schemas import RaceSummaryRequest, RaceSummaryResponse


class RaceDomainService:
    def __init__(
        self,
        repository: RaceRepository,
        progression_repository: ProgressionRepository | None = None,
        achievement_repository: AchievementRepository | None = None,
    ) -> None:
        self._repository = repository
        self._progression_repository = progression_repository
        self._achievement_repository = achievement_repository

    async def persist_race(
        self,
        request: RaceSummaryRequest,
        account_id: uuid.UUID | None = None,
        session: AsyncSession | None = None,
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
            progression = await prog_service.award_xp(
                account_id=account_id,
                problems_correct=player.problems_correct,
                longest_streak=player.longest_streak,
                mode=request.mode,
                race_id=request.race_id,
            )
            response.progression = progression

            if self._achievement_repository is not None and session is not None:
                from app.achievements.domain_service import AchievementDomainService

                ach_service = AchievementDomainService(self._achievement_repository)
                event_data = {
                    "problems_correct": player.problems_correct,
                    "position": player.position,
                }
                new_achievements = await ach_service.evaluate_race_completed(
                    account_id, event_data, session
                )
                if progression.level_up is not None:
                    new_achievements += await ach_service.evaluate_level_up(
                        account_id, progression.level_up.new_level, session
                    )
                response.new_achievements = new_achievements

        return response
