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
        player = next(
            (p for p in request.participants if p.avatar_id == request.human_avatar_id),
            None,
        )
        if player is None:
            from app.shared.exceptions import ValidationError

            raise ValidationError(message="Human avatar is not a race participant.")
        avatar_id = uuid.UUID(player.avatar_id)
        problems_solved = len(request.answers) if request.mode == "training" else _OBSTACLE_COUNT
        response_ms_total = (
            sum(answer.response_time_ms for answer in request.answers)
            if request.answers
            else player.average_response_ms * problems_solved
        )
        is_win = player.position == 1
        is_podium = player.position is not None and player.position <= 3

        await self._repository.insert_session(
            account_id=account_id,
            child_profile_id=request.child_profile_id,
            avatar_id=avatar_id,
            race_id=request.race_id,
            mode=request.mode,
            finishing_position=player.position,
            problems_solved=problems_solved,
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
            problems_delta=problems_solved,
            correct_delta=player.problems_correct,
            response_ms_delta=response_ms_total,
            streak=player.longest_streak,
        )
        await self._repository.upsert_avatar_stats(
            avatar_id,
            account_id,
            request.child_profile_id,
            wins_delta=1 if is_win else 0,
            podiums_delta=1 if is_podium else 0,
            streak=player.longest_streak,
        )

    async def get_player_stats(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> PlayerStatsResponse:
        stats = (
            await self._repository.get_player_stats_for_child(account_id, child_profile_id)
            if child_profile_id is not None
            else await self._repository.get_player_stats(account_id)
        )
        operation_counts = (
            await self._repository.get_operation_counts(account_id, child_profile_id)
            if child_profile_id is not None
            else {}
        )
        favourite_operation = self._favourite_operation(operation_counts)
        if stats is None:
            return PlayerStatsResponse(
                player_id=str(account_id),
                total_races=0,
                total_problems_solved=0,
                correct_answers=0,
                accuracy_all_time=None,
                avg_response_ms=None,
                favourite_operation=favourite_operation,
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
            favourite_operation=favourite_operation,
            best_streak=stats.best_streak,
            updated_at=stats.updated_at,
        )

    async def get_avatar_stats(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID, avatar_id: uuid.UUID
    ) -> AvatarStatsResponse:
        from app.shared.exceptions import NotFoundError

        stats = await self._repository.get_avatar_stats(account_id, child_profile_id, avatar_id)
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

    async def get_history(
        self, account_id: uuid.UUID, page: int, child_profile_id: uuid.UUID | None = None
    ) -> HistoryResponse:
        sessions, total = await self._repository.get_history(account_id, page, child_profile_id)
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

    async def get_weekly_summary(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> WeeklySummaryResponse:
        now = datetime.now(UTC)
        since = now - timedelta(days=7)
        sessions = await self._repository.get_sessions_since(account_id, since, child_profile_id)
        operation_counts = (
            await self._repository.get_operation_counts(account_id, child_profile_id, since)
            if child_profile_id is not None
            else {}
        )
        strongest_operation, weakest_operation = self._operation_extremes(operation_counts)

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
            strongest_operation=strongest_operation,
            weakest_operation=weakest_operation,
            races_completed=len(sessions),
            xp_earned=total_xp,
        )

    async def get_personal_records(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> PersonalRecordsResponse:
        stats = (
            await self._repository.get_player_stats_for_child(account_id, child_profile_id)
            if child_profile_id is not None
            else await self._repository.get_player_stats(account_id)
        )
        best_accuracy = await self._repository.get_best_race_accuracy(account_id, child_profile_id)
        fastest = await self._repository.get_fastest_avg_response_ms(account_id, child_profile_id)
        return PersonalRecordsResponse(
            best_streak=stats.best_streak if stats else 0,
            best_race_accuracy=best_accuracy,
            fastest_avg_response_ms=fastest,
            total_races=stats.total_races if stats else 0,
        )

    async def get_all_sessions(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> list[RaceSession]:
        return await self._repository.get_all_sessions(account_id, child_profile_id)

    @staticmethod
    def _favourite_operation(counts: dict[str, tuple[int, int]]) -> str | None:
        if not counts:
            return None
        highest_attempts = max(attempts for attempts, _ in counts.values())
        return min(
            operation for operation, (attempts, _) in counts.items() if attempts == highest_attempts
        )

    @staticmethod
    def _operation_extremes(
        counts: dict[str, tuple[int, int]],
    ) -> tuple[str | None, str | None]:
        accuracies = {
            operation: correct / attempts
            for operation, (attempts, correct) in counts.items()
            if attempts > 0
        }
        strongest = (
            min(op for op, accuracy in accuracies.items() if accuracy == max(accuracies.values()))
            if accuracies
            else None
        )
        eligible_for_weakest = {
            op: accuracy for op, accuracy in accuracies.items() if counts[op][0] >= 5
        }
        weakest = (
            min(
                op
                for op, accuracy in eligible_for_weakest.items()
                if accuracy == min(eligible_for_weakest.values())
            )
            if eligible_for_weakest
            else None
        )
        return strongest, weakest
