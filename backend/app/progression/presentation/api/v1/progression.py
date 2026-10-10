from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.auth import get_current_account
from app.presentation.api.middleware.child_profile import get_active_child_profile
from app.progression.domain_service import ProgressionDomainService
from app.progression.repository import SQLAlchemyProgressionRepository
from app.progression.schemas import ProgressionResponse
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/progression", tags=["progression"])


@router.get("", response_model=ProgressionResponse, status_code=200)
async def get_progression(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> ProgressionResponse:
    repo = SQLAlchemyProgressionRepository(session)
    service = ProgressionDomainService(repo)
    return await service.get_progression(account.id, child_profile.id)
