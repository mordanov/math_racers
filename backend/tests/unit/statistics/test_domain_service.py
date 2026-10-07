from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.races.schemas import ParticipantSummaryRequest, RaceSummaryRequest
from app.statistics.models import AvatarStats, PlayerStats, RaceSession

pytestmark = pytest.mark.unit

_NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)
_ACCOUNT_ID = uuid.uuid4()
_AVATAR_ID = uuid.uuid4()


def _make_request(
    *,
    mode: str = "quick",
    position: int | None = 1,
    problems_correct: int = 7,
    streak: int = 5,
    avg_ms: int = 1500,
) -> RaceSummaryRequest:
    return RaceSummaryRequest(
        race_id=uuid.uuid4(),
        seed="42",
        difficulty_tier=3,
        mode=mode,
        started_at=_NOW - timedelta(minutes=2),
        completed_at=_NOW,
        participants=[
            ParticipantSummaryRequest(
                avatar_id=str(_AVATAR_ID),
                position=position,
                problems_correct=problems_correct,
                longest_streak=streak,
                average_response_ms=avg_ms,
                total_distance=144,
                xp_earned=100,
            )
        ],
    )


def _make_repo() -> MagicMock:
    repo = MagicMock()
    repo.insert_session = AsyncMock()
    repo.upsert_player_stats = AsyncMock()
    repo.upsert_avatar_stats = AsyncMock()
    repo.get_player_stats = AsyncMock(return_value=None)
    repo.get_avatar_stats = AsyncMock(return_value=None)
    repo.get_avatar_stats_for_player = AsyncMock(return_value=[])
    repo.get_history = AsyncMock(return_value=([], 0))
    repo.get_sessions_since = AsyncMock(return_value=[])
    repo.get_all_sessions = AsyncMock(return_value=[])
    repo.get_best_race_accuracy = AsyncMock(return_value=None)
    repo.get_fastest_avg_response_ms = AsyncMock(return_value=None)
    return repo


async def test_update_on_race_calls_all_three_steps() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    request = _make_request()

    await service.update_on_race(_ACCOUNT_ID, request)

    repo.insert_session.assert_called_once()
    repo.upsert_player_stats.assert_called_once()
    repo.upsert_avatar_stats.assert_called_once()


async def test_update_on_race_win_increments_wins_and_podiums() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    await service.update_on_race(_ACCOUNT_ID, _make_request(position=1))

    _, kwargs = repo.upsert_avatar_stats.call_args
    assert kwargs["wins_delta"] == 1
    assert kwargs["podiums_delta"] == 1


async def test_update_on_race_third_place_increments_podium_not_win() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    await service.update_on_race(_ACCOUNT_ID, _make_request(position=3))

    _, kwargs = repo.upsert_avatar_stats.call_args
    assert kwargs["wins_delta"] == 0
    assert kwargs["podiums_delta"] == 1


async def test_update_on_race_training_mode_no_wins_no_podiums() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    await service.update_on_race(
        _ACCOUNT_ID, _make_request(mode="training", position=None)
    )

    _, kwargs = repo.upsert_avatar_stats.call_args
    assert kwargs["wins_delta"] == 0
    assert kwargs["podiums_delta"] == 0


async def test_update_on_race_player_stats_uses_correct_deltas() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    await service.update_on_race(
        _ACCOUNT_ID, _make_request(problems_correct=6, avg_ms=2000)
    )

    _, kwargs = repo.upsert_player_stats.call_args
    assert kwargs["races_delta"] == 1
    assert kwargs["problems_delta"] == 8  # OBSTACLE_COUNT
    assert kwargs["correct_delta"] == 6
    assert kwargs["response_ms_delta"] == 2000 * 8  # avg_ms * problems_solved


async def test_get_player_stats_returns_zeros_when_no_rows() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    result = await service.get_player_stats(_ACCOUNT_ID)

    assert result.total_races == 0
    assert result.accuracy_all_time is None
    assert result.avg_response_ms is None


async def test_get_player_stats_computes_accuracy_correctly() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    mock_stats = MagicMock(spec=PlayerStats)
    mock_stats.total_races = 5
    mock_stats.total_problems_solved = 40
    mock_stats.correct_answers = 36
    mock_stats.total_response_ms = 40 * 1800
    mock_stats.best_streak = 8
    mock_stats.updated_at = _NOW

    repo = _make_repo()
    repo.get_player_stats = AsyncMock(return_value=mock_stats)
    service = StatisticsDomainService(repo)
    result = await service.get_player_stats(_ACCOUNT_ID)

    assert result.accuracy_all_time == pytest.approx(36 / 40)
    assert result.avg_response_ms == 1800


async def test_get_weekly_summary_returns_zeros_when_no_sessions() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    repo = _make_repo()
    service = StatisticsDomainService(repo)
    result = await service.get_weekly_summary(_ACCOUNT_ID)

    assert result.races_completed == 0
    assert result.problems_solved == 0
    assert result.accuracy is None
    assert result.avg_response_ms is None
    assert result.strongest_operation is None
    assert result.weakest_operation is None


async def test_get_weekly_summary_aggregates_sessions() -> None:
    from app.statistics.domain_service import StatisticsDomainService

    def _session(problems: int, correct: int, xp: int, ms: int) -> MagicMock:
        s = MagicMock(spec=RaceSession)
        s.problems_solved = problems
        s.correct_answers = correct
        s.xp_earned = xp
        s.avg_response_ms = ms
        return s

    sessions = [
        _session(8, 7, 100, 1500),
        _session(8, 6, 80, 2000),
    ]

    repo = _make_repo()
    repo.get_sessions_since = AsyncMock(return_value=sessions)
    service = StatisticsDomainService(repo)
    result = await service.get_weekly_summary(_ACCOUNT_ID)

    assert result.races_completed == 2
    assert result.problems_solved == 16
    assert result.correct_answers == 13
    assert result.xp_earned == 180
    assert result.accuracy == pytest.approx(13 / 16)
    # avg_ms = (1500*8 + 2000*8) / 16 = (12000 + 16000) / 16 = 1750
    assert result.avg_response_ms == 1750
