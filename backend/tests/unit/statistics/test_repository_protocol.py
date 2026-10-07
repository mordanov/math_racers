from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_player_stats_has_required_columns() -> None:
    from app.statistics.models import PlayerStats

    for col in (
        "account_id",
        "total_races",
        "total_problems_solved",
        "correct_answers",
        "total_response_ms",
        "best_streak",
        "updated_at",
    ):
        assert hasattr(PlayerStats, col), f"PlayerStats missing: {col}"


def test_avatar_stats_has_required_columns() -> None:
    from app.statistics.models import AvatarStats

    for col in (
        "avatar_id",
        "account_id",
        "total_races",
        "wins",
        "podiums",
        "best_streak",
        "last_race_at",
    ):
        assert hasattr(AvatarStats, col), f"AvatarStats missing: {col}"


def test_race_session_has_required_columns() -> None:
    from app.statistics.models import RaceSession

    for col in (
        "id",
        "account_id",
        "avatar_id",
        "race_id",
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
    ):
        assert hasattr(RaceSession, col), f"RaceSession missing: {col}"
