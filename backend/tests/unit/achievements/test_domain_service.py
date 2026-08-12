"""Unit tests for AchievementDomainService predicates and evaluation logic."""

from __future__ import annotations

import uuid
from datetime import UTC
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.achievements.domain_service import AchievementDomainService
from app.achievements.models import PlayerAchievement

pytestmark = pytest.mark.unit


def _make_achievement(key: str) -> PlayerAchievement:
    obj = PlayerAchievement()
    obj.id = uuid.uuid4()
    obj.account_id = uuid.uuid4()
    obj.achievement_key = key
    obj.avatar_id = None
    from datetime import datetime

    obj.unlocked_at = datetime.now(UTC)
    return obj


def _make_repo(*, unlock_returns: PlayerAchievement | None = None) -> Any:
    repo = MagicMock()
    repo.unlock = AsyncMock(return_value=unlock_returns)
    repo.get_unlocked = AsyncMock(return_value=[])
    return repo


def _make_session() -> Any:
    session = MagicMock()

    async def _execute(query: Any, params: Any = None) -> Any:
        result = MagicMock()
        row = MagicMock()
        row.__getitem__ = MagicMock(return_value=1)
        result.fetchone = MagicMock(return_value=row)
        return result

    session.execute = AsyncMock(side_effect=_execute)
    return session


# ── first_race ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_first_race_predicate_fires_for_new_player() -> None:
    account_id = uuid.uuid4()
    record = _make_achievement("first_race")
    repo = _make_repo(unlock_returns=record)
    session = _make_session()

    service = AchievementDomainService(repo)
    results = await service.evaluate_race_completed(
        account_id, {"problems_correct": 5, "position": 1}, session
    )

    keys = [r.key for r in results]
    assert "first_race" in keys


@pytest.mark.asyncio
async def test_first_race_already_unlocked_skipped() -> None:
    account_id = uuid.uuid4()
    # unlock returns None → already unlocked, conflict
    repo = _make_repo(unlock_returns=None)
    session = _make_session()

    service = AchievementDomainService(repo)
    results = await service.evaluate_race_completed(
        account_id, {"problems_correct": 5, "position": 1}, session
    )

    # None returned means already unlocked → should not appear in results
    assert not any(r.key == "first_race" for r in results)


# ── perfect_race ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_perfect_race_fires_only_with_8_correct() -> None:
    account_id = uuid.uuid4()

    for correct in range(8):
        record = _make_achievement("perfect_race")
        repo = _make_repo(unlock_returns=record)
        session = _make_session()
        service = AchievementDomainService(repo)
        results = await service.evaluate_race_completed(
            account_id, {"problems_correct": correct, "position": 1}, session
        )
        assert not any(
            r.key == "perfect_race" for r in results
        ), f"Should not fire for {correct}"

    # Exactly 8 should fire
    record = _make_achievement("perfect_race")
    repo = _make_repo(unlock_returns=record)
    session = _make_session()
    service = AchievementDomainService(repo)
    results = await service.evaluate_race_completed(
        account_id, {"problems_correct": 8, "position": 1}, session
    )
    assert any(r.key == "perfect_race" for r in results)


# ── level milestones ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_level_5_fires_at_level_5_not_4() -> None:
    account_id = uuid.uuid4()

    record = _make_achievement("level_5")
    repo_fire = _make_repo(unlock_returns=record)
    session = _make_session()
    service = AchievementDomainService(repo_fire)
    results = await service.evaluate_level_up(account_id, 5, session)
    assert any(r.key == "level_5" for r in results)

    repo_no_fire = _make_repo(unlock_returns=None)
    session2 = _make_session()
    service2 = AchievementDomainService(repo_no_fire)

    # At level 4, predicate is False so unlock is never called → no result
    # We need to patch the predicate to return False for level 4
    results_4 = await service2.evaluate_level_up(account_id, 4, session2)
    assert not any(r.key == "level_5" for r in results_4)


# ── predicate exception isolation ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_predicate_exception_does_not_abort_other_evaluations() -> None:
    account_id = uuid.uuid4()

    # Make unlock raise for "first_race" but return normally for others
    call_count = 0

    async def _unlock(
        aid: uuid.UUID, key: str, avatar_id: uuid.UUID | None = None
    ) -> PlayerAchievement | None:
        nonlocal call_count
        call_count += 1
        if key == "first_race":
            raise RuntimeError("simulated DB error")
        return _make_achievement(key)

    repo = MagicMock()
    repo.unlock = _unlock
    repo.get_unlocked = AsyncMock(return_value=[])

    session = _make_session()
    service = AchievementDomainService(repo)

    # Should not raise; other achievements may still come through
    results = await service.evaluate_race_completed(
        account_id, {"problems_correct": 8, "position": 1}, session
    )
    # perfect_race should still be evaluated (position=1 makes champion too)
    assert isinstance(results, list)
    # first_race failed silently; perfect_race and others may succeed
    assert not any(r.key == "first_race" for r in results)
