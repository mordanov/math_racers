"""Unit tests for opponent personality constants and schema."""

from __future__ import annotations

import pytest

from app.opponents.personalities import PERSONALITIES

VALID_SPEED_PROFILES = {"uniform", "front_loaded", "back_loaded", "random"}


def test_personalities_count() -> None:
    assert len(PERSONALITIES) == 5


def test_personality_ids_are_unique() -> None:
    ids = [p.id for p in PERSONALITIES]
    assert len(ids) == len(set(ids))


def test_accuracy_rates_in_range() -> None:
    for p in PERSONALITIES:
        assert 0.0 <= p.accuracy_rate <= 1.0, f"{p.id} accuracy_rate out of range"


def test_speed_profiles_are_valid() -> None:
    for p in PERSONALITIES:
        assert (
            p.speed_profile in VALID_SPEED_PROFILES
        ), f"{p.id} has invalid speed_profile"


def test_speedster_tier_offset() -> None:
    speedster = next(p for p in PERSONALITIES if p.id == "speedster")
    assert speedster.tier_offset == 1


def test_schema_serialises_with_camel_case() -> None:
    p = PERSONALITIES[0]
    data = p.model_dump(by_alias=True)
    assert "accuracyRate" in data
    assert "accuracy_rate" not in data
    assert "baseResponseTimeMs" in data
    assert "responseTimeVarianceMs" in data
    assert "speedProfile" in data
    assert "tierOffset" in data


@pytest.mark.unit
def test_all_personalities_have_non_empty_names() -> None:
    for p in PERSONALITIES:
        assert p.name, f"{p.id} has empty name"
