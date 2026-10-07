from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.races.schemas import RaceSummaryRequest
    from app.statistics.repository import StatisticsRepository

from app.statistics.models import RaceSession
from app.statistics.schemas import (
    AvatarStatsResponse,
    HistoryResponse,
    PersonalRecordsResponse,
    PlayerStatsResponse,
    RaceSessionResponse,
    WeeklySummaryResponse,
)

_OBSTACLE_COUNT = 8  # game constant — matches frontend OBSTACLE_COUNT


class StatisticsDomainService:
    def __init__(self, repository: StatisticsRepository) -> None:
        self._repository = repository

    async def update_on_race(
        self,
        account_id: uuid.UUID,
        request: RaceSummaryRequest,
    ) -> None:
        player = request.participants[0]
        avatar_id = uuid.UUID(player.avatar_id)
        is_win = player.position == 1
        is_podium = player.position is not None and player.position <= 3

        await self._repository.insert_session(
            account_id=account_id,
            avatar_id=avatar_id,
            race_id=request.race_id,
            mode=request.mode,
            finishing_position=player.position,
            problems_solved=_OBSTACLE_COUNT,
            correct_answers=player.problems_correct,
            difficulty_tier=request.difficulty_tier,
            xp_earned=player.xp_earned,
            avg_response_ms=player.average_response_ms,
            longest_streak=player.longest_streak,
            started_at=request.started_at,
            finished_at=request.completed_at,
        )
        await self._repository.upsert_player_stats(
            account_id,
            races_delta=1,
            problems_delta=_OBSTACLE_COUNT,
            correct_delta=player.problems_correct,
            response_ms_delta=player.average_response_ms * _OBSTACLE_COUNT,
            streak=player.longest_streak,
        )
        await self._repository.upsert_avatar_stats(
            avatar_id,
            account_id,
            wins_delta=1 if is_win else 0,
            podiums_delta=1 if is_podium else 0,
            streak=player.longest_streak,
        )

    async def get_player_stats(self, account_id: uuid.UUID) -> PlayerStatsResponse:
        stats = await self._repository.get_player_stats(account_id)
        if stats is None:
            return PlayerStatsResponse(
                player_id=str(account_id),
                total_races=0,
                total_problems_solved=0,
                correct_answers=0,
                accuracy_all_time=None,
                avg_response_ms=None,
                best_streak=0,
                updated_at=datetime.now(UTC),
            )
        accuracy = (
            stats.correct_answers / stats.total_problems_solved
            if stats.total_problems_solved > 0
            else None
        )
        avg_ms = (
            stats.total_response_ms // stats.total_problems_solved
            if stats.total_problems_solved > 0
            else None
        )
        return PlayerStatsResponse(
            player_id=str(account_id),
            total_races=stats.total_races,
            total_problems_solved=stats.total_problems_solved,
            correct_answers=stats.correct_answers,
            accuracy_all_time=accuracy,
            avg_response_ms=avg_ms,
            best_streak=stats.best_streak,
            updated_at=stats.updated_at,
        )

    async def get_avatar_stats(self, avatar_id: uuid.UUID) -> AvatarStatsResponse:
        from app.shared.exceptions import NotFoundError

        stats = await self._repository.get_avatar_stats(avatar_id)
        if stats is None:
            raise NotFoundError(message=f"No stats found for avatar {avatar_id}")
        return AvatarStatsResponse(
            avatar_id=str(stats.avatar_id),
            player_id=str(stats.account_id),
            total_races=stats.total_races,
            wins=stats.wins,
            podiums=stats.podiums,
            best_streak=stats.best_streak,
            last_race_at=stats.last_race_at,
        )

    async def get_history(self, account_id: uuid.UUID, page: int) -> HistoryResponse:
        sessions, total = await self._repository.get_history(account_id, page)
        total_pages = max(1, math.ceil(total / 20))
        return HistoryResponse(
            results=[
                RaceSessionResponse(
                    id=str(s.id),
                    avatar_id=str(s.avatar_id),
                    mode=s.mode,
                    finishing_position=s.finishing_position,
                    problems_solved=s.problems_solved,
                    correct_answers=s.correct_answers,
                    mistakes=s.problems_solved - s.correct_answers,
                    difficulty_tier=s.difficulty_tier,
                    xp_earned=s.xp_earned,
                    avg_response_ms=s.avg_response_ms,
                    longest_streak=s.longest_streak,
                    started_at=s.started_at,
                    finished_at=s.finished_at,
                )
                for s in sessions
            ],
            page=page,
            total_pages=total_pages,
            total_records=total,
        )

    async def get_weekly_summary(self, account_id: uuid.UUID) -> WeeklySummaryResponse:
        now = datetime.now(UTC)
        since = now - timedelta(days=7)
        sessions = await self._repository.get_sessions_since(account_id, since)

        total_problems = sum(s.problems_solved for s in sessions)
        total_correct = sum(s.correct_answers for s in sessions)
        total_xp = sum(s.xp_earned for s in sessions)
        total_response_ms = sum(s.avg_response_ms * s.problems_solved for s in sessions)

        accuracy = total_correct / total_problems if total_problems > 0 else None
        avg_ms = total_response_ms // total_problems if total_problems > 0 else None

        return WeeklySummaryResponse(
            period_start=since,
            period_end=now,
            problems_solved=total_problems,
            correct_answers=total_correct,
            accuracy=accuracy,
            avg_response_ms=avg_ms,
            races_completed=len(sessions),
            xp_earned=total_xp,
        )

    async def get_personal_records(self, account_id: uuid.UUID) -> PersonalRecordsResponse:
        stats = await self._repository.get_player_stats(account_id)
        best_accuracy = await self._repository.get_best_race_accuracy(account_id)
        fastest = await self._repository.get_fastest_avg_response_ms(account_id)
        return PersonalRecordsResponse(
            best_streak=stats.best_streak if stats else 0,
            best_race_accuracy=best_accuracy,
            fastest_avg_response_ms=fastest,
            total_races=stats.total_races if stats else 0,
        )

    async def get_all_sessions(self, account_id: uuid.UUID) -> list[RaceSession]:
        return await self._repository.get_all_sessions(account_id)
