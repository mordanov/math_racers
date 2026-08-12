"""Unit tests for the static achievement catalogue."""

from __future__ import annotations

import pytest

from app.achievements.catalogue import CATALOGUE, VALID_CATEGORIES, get_by_key

pytestmark = pytest.mark.unit


def test_no_duplicate_keys() -> None:
    keys = [a.key for a in CATALOGUE]
    assert len(keys) == len(set(keys)), "Duplicate achievement keys found"


def test_all_required_fields_present() -> None:
    for entry in CATALOGUE:
        assert entry.key, f"Missing key: {entry}"
        assert entry.category, f"Missing category: {entry.key}"
        assert entry.title, f"Missing title: {entry.key}"
        assert entry.description, f"Missing description: {entry.key}"
        assert entry.icon_path, f"Missing icon_path: {entry.key}"


def test_all_categories_valid() -> None:
    for entry in CATALOGUE:
        assert (
            entry.category in VALID_CATEGORIES
        ), f"Invalid category '{entry.category}' for key '{entry.key}'"


def test_icon_paths_have_expected_format() -> None:
    for entry in CATALOGUE:
        assert entry.icon_path.startswith(
            "assets/achievements/"
        ), f"icon_path does not start with 'assets/achievements/': {entry.icon_path}"
        assert entry.icon_path.endswith(
            ".png"
        ), f"icon_path does not end with '.png': {entry.icon_path}"


def test_get_by_key_returns_correct_entry() -> None:
    entry = get_by_key("first_race")
    assert entry is not None
    assert entry.key == "first_race"


def test_get_by_key_returns_none_for_unknown() -> None:
    assert get_by_key("nonexistent_key") is None


def test_catalogue_has_expected_keys() -> None:
    keys = {a.key for a in CATALOGUE}
    expected = {
        "first_race",
        "perfect_race",
        "podium_finisher",
        "champion",
        "level_5",
        "level_10",
        "level_20",
    }
    assert expected.issubset(keys)
