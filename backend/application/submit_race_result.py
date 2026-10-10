from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.races.domain_service import RaceDomainService
    from app.races.schemas import RaceResultRequest, RaceSummaryResponse


class SubmitRaceResultUseCase:
    def __init__(self, race_service: RaceDomainService) -> None:
        self._race_service = race_service

    async def execute(
        self,
        race_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceResultRequest,
        session: AsyncSession,
    ) -> RaceSummaryResponse:
        return await self._race_service.submit_result(
            race_id,
            account_id,
            child_profile_id,
            request,
            session,
        )
