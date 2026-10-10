"""Unit tests for tier selection logic."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.mathematics.difficulty import select_tier
from app.mathematics.schemas import Tier6Settings


def test_advances_tier_at_high_skill() -> None:
    assert select_tier(2, 0.90) == 3
    assert select_tier(2, 0.95) == 3
    assert select_tier(2, 1.0) == 3


def test_decreases_tier_at_low_skill() -> None:
    assert select_tier(3, 0.59) == 2
    assert select_tier(3, 0.0) == 2


def test_maintains_tier_in_middle_range() -> None:
    assert select_tier(3, 0.60) == 3
    assert select_tier(3, 0.75) == 3
    assert select_tier(3, 0.89) == 3


def test_does_not_advance_beyond_tier_6() -> None:
    assert select_tier(6, 1.0) == 6


def test_does_not_decrease_below_tier_1() -> None:
    assert select_tier(1, 0.0) == 1


def test_parent_override_takes_precedence() -> None:
    assert select_tier(2, 0.95, parent_override=4) == 4
    assert select_tier(5, 0.1, parent_override=3) == 3


def test_parent_override_is_clamped() -> None:
    assert select_tier(3, 0.5, parent_override=7) == 6
    assert select_tier(3, 0.5, parent_override=0) == 1
    assert select_tier(3, 0.5, parent_override=-5) == 1


def test_tier6_settings_accept_unique_supported_operations() -> None:
    settings = Tier6Settings(
        operations=["addition", "division"],
        min_operand=2,
        max_operand=30,
    )

    assert settings.operations == ["addition", "division"]


@pytest.mark.parametrize(
    "data",
    [
        {"operations": [], "min_operand": 1, "max_operand": 10},
        {"operations": ["unknown"], "min_operand": 1, "max_operand": 10},
        {"operations": ["addition", "addition"], "min_operand": 1, "max_operand": 10},
        {"operations": ["addition"], "min_operand": 20, "max_operand": 10},
        {"operations": ["addition"], "min_operand": 0, "max_operand": 10},
    ],
)
def test_tier6_settings_reject_invalid_values(data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Tier6Settings.model_validate(data)
