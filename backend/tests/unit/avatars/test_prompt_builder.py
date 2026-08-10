import pytest

from app.avatars.prompt_builder import PROMPT_VERSION, VersionedPrompt, build_character_prompt

_BASE_METADATA = {
    "species": "fox",
    "fur_color": "#FF6600",
    "eye_color": "#00AAFF",
    "hairstyle": "spiky",
    "accessories": ["glasses", "scarf"],
    "clothes_top_color": "#4169E1",
    "clothes_bottom_color": "#FFFFFF",
    "personality": "curious and energetic",
    "appearance_summary": "A quick, cheerful fox with bright eyes.",
}


def test_returns_versioned_prompt():
    result = build_character_prompt(_BASE_METADATA)
    assert isinstance(result, VersionedPrompt)
    assert result.prompt_version == PROMPT_VERSION
    assert result.attempt == 1


def test_attempt1_includes_accessories():
    result = build_character_prompt(_BASE_METADATA, attempt=1)
    assert "glasses" in result.text
    assert "scarf" in result.text


def test_attempt2_excludes_accessories():
    result = build_character_prompt(_BASE_METADATA, attempt=2)
    assert "glasses" not in result.text
    assert "scarf" not in result.text
    assert result.attempt == 2


def test_attempt3_includes_accessories_and_stricter_negative():
    result = build_character_prompt(_BASE_METADATA, attempt=3)
    assert "glasses" in result.text
    assert "inappropriate clothing" in result.text
    assert result.attempt == 3


def test_no_accessories_metadata():
    metadata = {**_BASE_METADATA, "accessories": []}
    result = build_character_prompt(metadata, attempt=1)
    assert "accessories" not in result.text or "none" not in result.text.lower()


def test_species_in_prompt():
    result = build_character_prompt(_BASE_METADATA)
    assert "fox" in result.text


def test_prompt_version_constant():
    assert PROMPT_VERSION == "1.0.0"


def test_defaults_used_for_missing_fields():
    result = build_character_prompt({}, attempt=1)
    assert isinstance(result.text, str)
    assert len(result.text) > 20


def test_all_attempts_return_prompt_version():
    for attempt in (1, 2, 3):
        result = build_character_prompt(_BASE_METADATA, attempt=attempt)
        assert result.prompt_version == PROMPT_VERSION


def test_attempt2_uses_simplified_template():
    result = build_character_prompt(_BASE_METADATA, attempt=2)
    assert "personality" not in result.text.lower() or "curious and energetic" not in result.text
