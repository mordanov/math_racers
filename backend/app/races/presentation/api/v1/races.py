from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.achievements.repository import SQLAlchemyAchievementRepository
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.auth import get_current_account
from app.presentation.api.middleware.child_profile import get_active_child_profile
from app.progression.repository import SQLAlchemyProgressionRepository
from app.races.domain_service import RaceDomainService
from app.races.repository import SQLAlchemyRaceRepository
from app.races.schemas import (
    RaceAnswerSubmitRequest,
    RaceAnswerSubmitResponse,
    RaceResultRequest,
    RaceSessionRequest,
    RaceSessionResponse,
    RaceSummaryResponse,
)
from app.statistics.domain_service import StatisticsDomainService
from app.statistics.repository import SQLAlchemyStatisticsRepository
from application.submit_race_result import SubmitRaceResultUseCase
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/races", tags=["races"])


@router.post("", response_model=RaceSessionResponse, status_code=201)
async def create_race(
    body: RaceSessionRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
    child_profile: ChildProfile = Depends(get_active_child_profile),
) -> RaceSessionResponse:
    race_repo = SQLAlchemyRaceRepository(session)
    return await RaceDomainService(race_repo).create_session(account.id, child_profile.id, body)


@router.post("/{race_id}/answers", response_model=RaceAnswerSubmitResponse)
async def submit_race_answer(
    race_id: uuid.UUID,
    body: RaceAnswerSubmitRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
    child_profile: ChildProfile = Depends(get_active_child_profile),
) -> RaceAnswerSubmitResponse:
    race_repo = SQLAlchemyRaceRepository(session)
    return await RaceDomainService(race_repo).submit_answer(
        race_id, account.id, child_profile.id, body
    )


@router.post("/{race_id}/results", response_model=RaceSummaryResponse)
async def submit_race_result(
    race_id: uuid.UUID,
    body: RaceResultRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
    child_profile: ChildProfile = Depends(get_active_child_profile),
) -> RaceSummaryResponse:
    race_repo = SQLAlchemyRaceRepository(session)
    service = RaceDomainService(
        race_repo,
        SQLAlchemyProgressionRepository(session),
        SQLAlchemyAchievementRepository(session),
        StatisticsDomainService(SQLAlchemyStatisticsRepository(session)),
    )
    return await SubmitRaceResultUseCase(service).execute(
        race_id, account.id, child_profile.id, body, session
    )
