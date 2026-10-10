from __future__ import annotations

import math
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.progression.domain_service import (
    ProgressionDomainService,
    _calculate_xp_delta,
    _compute_level,
    _xp_to_next_level,
)
from app.progression.models import PlayerProgression


def _mock_repo(total_xp: int | None = None) -> AsyncMock:
    repo = AsyncMock()
    current_total = total_xp or 0

    if total_xp is None:
        repo.get.return_value = None
    else:
        progression = MagicMock(spec=PlayerProgression)
        progression.total_xp = total_xp
        progression.current_level = _compute_level(total_xp)
        repo.get.return_value = progression

    async def add_xp(
        _account_id: uuid.UUID, amount: int, _child_profile_id: uuid.UUID | None = None
    ) -> tuple[int, int]:
        nonlocal current_total
        current_total += amount
        return current_total, _compute_level(current_total)

    repo.add_xp.side_effect = add_xp
    return repo


class TestXpFormula:
    def test_quick_race_no_streak(self) -> None:
        assert _calculate_xp_delta(5, 0, "quick") == 200  # 100 + 100 + 0 + 0

    def test_championship_race_has_no_completion_bonus(self) -> None:
        assert _calculate_xp_delta(5, 0, "championship") == 200

    def test_training_awards_only_correct_answer_xp(self) -> None:
        assert _calculate_xp_delta(5, 0, "training") == 100

    def test_streak_bonus(self) -> None:
        assert _calculate_xp_delta(0, 10, "quick") == 120  # 100 + 0 + 20 + 0

    def test_streak_partial(self) -> None:
        # streak of 4 gives floor(4/5)*10 = 0
        assert _calculate_xp_delta(0, 4, "quick") == 100

    def test_streak_five(self) -> None:
        # streak of 5 gives floor(5/5)*10 = 10
        assert _calculate_xp_delta(0, 5, "quick") == 110

    def test_combined(self) -> None:
        # 100 + 7*20 + floor(5/5)*10 + 0 = 100 + 140 + 10 = 250
        assert _calculate_xp_delta(7, 5, "quick") == 250

    def test_duel_no_bonus(self) -> None:
        assert _calculate_xp_delta(3, 0, "duel") == 160


class TestLevelFormula:
    @pytest.mark.parametrize(
        "total_xp,expected_level",
        [
            (0, 1),
            (99, 1),
            (100, 1),
            (399, 1),
            (400, 2),
            (899, 2),
            (900, 3),
            (2500, 5),
            (10000, 10),
        ],
    )
    def test_level_boundaries(self, total_xp: int, expected_level: int) -> None:
        assert _compute_level(total_xp) == expected_level

    def test_matches_formula(self) -> None:
        for xp in range(0, 5001, 50):
            assert _compute_level(xp) == max(1, math.floor(math.sqrt(xp / 100)))


class TestXpToNextLevel:
    def test_never_negative(self) -> None:
        for xp in range(0, 10001, 100):
            level = _compute_level(xp)
            result = _xp_to_next_level(xp, level)
            assert result >= 1, f"xp_to_next_level was {result} at total_xp={xp}"

    def test_at_exact_boundary(self) -> None:
        # At exactly 400 XP (level 2), next threshold is level 3 = 900
        assert _xp_to_next_level(400, 2) == 500

    def test_zero_xp(self) -> None:
        assert _xp_to_next_level(0, 1) == 400


class TestAwardXp:
    @pytest.mark.asyncio
    async def test_zero_xp_training_saves_no_xp_event(self) -> None:
        repo = _mock_repo(total_xp=0)

        result = await ProgressionDomainService(repo).award_xp(
            account_id=uuid.uuid4(),
            problems_correct=0,
            longest_streak=0,
            mode="training",
            race_id=uuid.uuid4(),
        )

        assert result.total_xp == 0
        assert result.current_level == 1
        repo.add_xp.assert_not_awaited()
        repo.insert_event.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_xp_awarded_from_zero(self) -> None:
        repo = _mock_repo(total_xp=None)
        service = ProgressionDomainService(repo)
        result = await service.award_xp(
            account_id=uuid.uuid4(),
            problems_correct=5,
            longest_streak=0,
            mode="quick",
            race_id=uuid.uuid4(),
        )
        assert result.xp_earned_this_race == 200
        repo.add_xp.assert_awaited_once()
        repo.insert_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_level_up_detected(self) -> None:
        repo = _mock_repo(total_xp=399)  # one XP away from level 2
        service = ProgressionDomainService(repo)
        result = await service.award_xp(
            account_id=uuid.uuid4(),
            problems_correct=0,
            longest_streak=0,
            mode="quick",
            race_id=uuid.uuid4(),
        )
        # 399 + 100 = 499 → level 2
        assert result.level_up is not None
        assert result.level_up.previous_level == 1
        assert result.level_up.new_level == 2

    @pytest.mark.asyncio
    async def test_no_level_up_within_level(self) -> None:
        repo = _mock_repo(total_xp=200)  # level 1
        service = ProgressionDomainService(repo)
        result = await service.award_xp(
            account_id=uuid.uuid4(),
            problems_correct=0,
            longest_streak=0,
            mode="quick",
            race_id=uuid.uuid4(),
        )
        # 200 + 100 = 300 → still level 1 (floor(sqrt(300/100))=1)
        assert result.level_up is None

    @pytest.mark.asyncio
    async def test_championship_race_does_not_award_completion_bonus(self) -> None:
        repo = _mock_repo(total_xp=0)
        service = ProgressionDomainService(repo)
        result = await service.award_xp(
            account_id=uuid.uuid4(),
            problems_correct=5,
            longest_streak=0,
            mode="championship",
            race_id=uuid.uuid4(),
        )
        assert result.xp_earned_this_race == 200

    @pytest.mark.asyncio
    async def test_training_awards_correct_answer_xp_without_race_xp(self) -> None:
        repo = _mock_repo(total_xp=0)
        service = ProgressionDomainService(repo)
        result = await service.award_xp(
            account_id=uuid.uuid4(),
            problems_correct=5,
            longest_streak=5,
            mode="training",
            race_id=uuid.uuid4(),
        )
        assert result.xp_earned_this_race == 100

    @pytest.mark.asyncio
    async def test_awards_xp_to_the_selected_child(self) -> None:
        account_id = uuid.uuid4()
        child_id = uuid.uuid4()
        race_id = uuid.uuid4()
        repo = _mock_repo(total_xp=50)

        await ProgressionDomainService(repo).award_xp(
            account_id=account_id,
            problems_correct=2,
            longest_streak=0,
            mode="training",
            race_id=race_id,
            child_profile_id=child_id,
        )

        repo.get.assert_not_awaited()
        repo.add_xp.assert_awaited_once_with(account_id, 40, child_id)
        repo.insert_event.assert_awaited_once_with(
            account_id, "race_completion", 40, race_id, child_id
        )

    @pytest.mark.asyncio
    async def test_championship_completion_bonus_is_awarded_once(self) -> None:
        account_id = uuid.uuid4()
        child_id = uuid.uuid4()
        championship_id = uuid.uuid4()
        repo = _mock_repo(total_xp=200)
        repo.insert_championship_bonus_event.return_value = True

        amount = await ProgressionDomainService(repo).award_championship_completion(
            account_id, child_id, championship_id
        )

        assert amount == 500
        repo.insert_championship_bonus_event.assert_awaited_once_with(
            account_id, child_id, championship_id
        )
        repo.add_xp.assert_awaited_once_with(account_id, 500, child_id)

    @pytest.mark.asyncio
    async def test_duplicate_championship_completion_does_not_award_xp(self) -> None:
        repo = _mock_repo(total_xp=200)
        repo.insert_championship_bonus_event.return_value = False

        amount = await ProgressionDomainService(repo).award_championship_completion(
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        )

        assert amount == 0
        repo.get.assert_not_awaited()
        repo.add_xp.assert_not_awaited()


class TestGetProgression:
    @pytest.mark.asyncio
    async def test_zero_state_when_no_row(self) -> None:
        repo = _mock_repo(total_xp=None)
        service = ProgressionDomainService(repo)
        result = await service.get_progression(uuid.uuid4())
        assert result.total_xp == 0
        assert result.current_level == 1
        assert result.xp_to_next_level == 400

    @pytest.mark.asyncio
    async def test_returns_existing_progression(self) -> None:
        repo = _mock_repo(total_xp=1450)
        service = ProgressionDomainService(repo)
        result = await service.get_progression(uuid.uuid4())
        assert result.total_xp == 1450
        assert result.current_level == 3
        assert result.xp_to_next_level == 150  # level 4 = 1600, 1600-1450=150
