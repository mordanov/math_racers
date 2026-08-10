from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.presentation.api.middleware.auth import get_current_account
from app.races.domain_service import RaceDomainService
from app.races.repository import SQLAlchemyRaceRepository
from app.races.schemas import RaceSummaryRequest, RaceSummaryResponse
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/races", tags=["races"])


@router.post("", response_model=RaceSummaryResponse, status_code=201)
async def create_race(
    body: RaceSummaryRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> RaceSummaryResponse:
    repo = SQLAlchemyRaceRepository(session)
    service = RaceDomainService(repo)
    return await service.persist_race(body)
