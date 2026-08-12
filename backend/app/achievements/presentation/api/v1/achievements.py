from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account, AccountRole
from app.achievements.catalogue import get_by_key
from app.achievements.domain_service import AchievementDomainService
from app.achievements.repository import SQLAlchemyAchievementRepository
from app.achievements.schemas import (
    AchievementListResponse,
    PlayerAchievementListResponse,
    PlayerAchievementResponse,
)
from app.presentation.api.middleware.auth import get_current_account
from app.shared.exceptions import PermissionError
from infrastructure.database.session import get_session

router = APIRouter(tags=["achievements"])


@router.get(
    "/api/v1/achievements", response_model=AchievementListResponse, status_code=200
)
async def get_achievements(
    account_id: uuid.UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> AchievementListResponse:
    repo = SQLAlchemyAchievementRepository(session)
    service = AchievementDomainService(repo)
    achievements = await service.get_visible_catalogue(account_id, session)
    return AchievementListResponse(achievements=achievements)


@router.get(
    "/api/v1/players/{account_id}/achievements",
    response_model=PlayerAchievementListResponse,
    status_code=200,
)
async def get_player_achievements(
    account_id: uuid.UUID,
    current_account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> PlayerAchievementListResponse:
    if (
        current_account.id != account_id
        and current_account.role != AccountRole.administrator
    ):
        raise PermissionError(message="You may only view your own achievements.")

    repo = SQLAlchemyAchievementRepository(session)
    records = await repo.get_unlocked(account_id)

    achievements: list[PlayerAchievementResponse] = []
    for record in records:
        defn = get_by_key(record.achievement_key)
        if defn is None:
            continue
        achievements.append(
            PlayerAchievementResponse(
                key=defn.key,
                category=defn.category,
                title=defn.title,
                description=defn.description,
                hidden=defn.hidden,
                icon_path=defn.icon_path,
                unlocked_at=record.unlocked_at,
                avatar_id=record.avatar_id,
            )
        )

    return PlayerAchievementListResponse(
        account_id=account_id, achievements=achievements
    )
