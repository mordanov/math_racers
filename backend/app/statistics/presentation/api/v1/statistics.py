from __future__ import annotations

import csv
import io
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account, AccountRole
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.auth import get_current_account
from app.presentation.api.middleware.child_profile import get_active_child_profile
from app.shared.exceptions import PermissionError
from app.statistics.domain_service import StatisticsDomainService
from app.statistics.repository import SQLAlchemyStatisticsRepository
from app.statistics.schemas import (
    AvatarStatsResponse,
    HistoryResponse,
    PersonalRecordsResponse,
    PlayerStatsResponse,
    WeeklySummaryResponse,
)
from infrastructure.database.session import get_session

router = APIRouter(tags=["statistics"])


def _check_access(account: Account, account_id: uuid.UUID) -> None:
    if account.role != AccountRole.administrator and account.id != account_id:
        raise PermissionError(message="Access denied")


def _service(session: AsyncSession) -> StatisticsDomainService:
    return StatisticsDomainService(SQLAlchemyStatisticsRepository(session))


# --- "me" routes (frontend uses these) ---


@router.get("/api/v1/players/me/statistics", response_model=PlayerStatsResponse)
async def get_my_statistics(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> PlayerStatsResponse:
    return await _service(session).get_player_stats(account.id, child_profile.id)


@router.get("/api/v1/players/me/history", response_model=HistoryResponse)
async def get_my_history(
    page: int = Query(default=1, ge=1),
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> HistoryResponse:
    return await _service(session).get_history(account.id, page, child_profile.id)


@router.get("/api/v1/players/me/weekly-summary", response_model=WeeklySummaryResponse)
async def get_my_weekly_summary(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> WeeklySummaryResponse:
    return await _service(session).get_weekly_summary(account.id, child_profile.id)


@router.get("/api/v1/players/me/personal-records", response_model=PersonalRecordsResponse)
async def get_my_personal_records(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> PersonalRecordsResponse:
    return await _service(session).get_personal_records(account.id, child_profile.id)


@router.get("/api/v1/players/me/export")
async def export_my_csv(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    sessions = await _service(session).get_all_sessions(account.id, child_profile.id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "avatar_id",
            "mode",
            "finishing_position",
            "problems_solved",
            "correct_answers",
            "difficulty_tier",
            "xp_earned",
            "avg_response_ms",
            "longest_streak",
            "started_at",
            "finished_at",
        ]
    )
    for s in sessions:
        writer.writerow(
            [
                str(s.id),
                str(s.avatar_id),
                s.mode,
                s.finishing_position,
                s.problems_solved,
                s.correct_answers,
                s.difficulty_tier,
                s.xp_earned,
                s.avg_response_ms,
                s.longest_streak,
                s.started_at.isoformat(),
                s.finished_at.isoformat(),
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=statistics_{account.id}.csv"},
    )


# --- explicit account_id routes (for admin access) ---


@router.get("/api/v1/players/{account_id}/statistics", response_model=PlayerStatsResponse)
async def get_player_statistics(
    account_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> PlayerStatsResponse:
    _check_access(account, account_id)
    return await _service(session).get_player_stats(account_id)


@router.get(
    "/api/v1/players/{account_id}/avatars/{avatar_id}/statistics",
    response_model=AvatarStatsResponse,
)
async def get_avatar_statistics(
    account_id: uuid.UUID,
    avatar_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> AvatarStatsResponse:
    _check_access(account, account_id)
    return await _service(session).get_avatar_stats(account_id, child_profile.id, avatar_id)


@router.get("/api/v1/players/{account_id}/history", response_model=HistoryResponse)
async def get_history(
    account_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> HistoryResponse:
    _check_access(account, account_id)
    return await _service(session).get_history(account_id, page)


@router.get("/api/v1/players/{account_id}/weekly-summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    account_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> WeeklySummaryResponse:
    _check_access(account, account_id)
    return await _service(session).get_weekly_summary(account_id)


@router.get(
    "/api/v1/players/{account_id}/personal-records",
    response_model=PersonalRecordsResponse,
)
async def get_personal_records(
    account_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> PersonalRecordsResponse:
    _check_access(account, account_id)
    return await _service(session).get_personal_records(account_id)
