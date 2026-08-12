from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROMPT_VERSION = "1.0.0"

_GLOBAL_PREFIX = (
    "Children's educational cartoon style, vibrant colours, friendly and approachable, "
    "no shadows, flat clean lines, suitable for ages 6-12."
)

_GLOBAL_NEGATIVE = (
    "realistic, photo, dark, scary, violent, weapons, text, watermark, "
    "signature, border, frame, cropped, multiple characters"
)

_CHARACTER_TEMPLATE = (
    "{prefix} "
    "A {species} character with {fur_color} fur, {eye_color} eyes, {hairstyle} hairstyle"
    "{accessories_part}, "
    "wearing {top_color} top and {bottom_color} shorts, "
    "running pose, full body, transparent background, 1024x1024. "
    "Personality: {personality}. {appearance_summary}. "
    "Negative: {negative}"
)

_SIMPLIFIED_TEMPLATE = (
    "{prefix} "
    "A {species} character with {fur_color} fur, {eye_color} eyes, {hairstyle} hairstyle, "
    "wearing {top_color} top and {bottom_color} shorts, "
    "running pose, full body, transparent background, 1024x1024. "
    "Negative: {negative}"
)

_STRICT_EXTRA_NEGATIVE = (
    ", text, numbers, letters, watermark, logo, brand, adult content, "
    "inappropriate clothing, political symbols, religious symbols"
)


@dataclass(frozen=True)
class VersionedPrompt:
    text: str
    prompt_version: str
    attempt: int


def build_character_prompt(
    metadata: dict[str, Any], attempt: int = 1
) -> VersionedPrompt:
    """Build a deterministic image generation prompt from avatar metadata.

    attempt=1: full prompt with all variables
    attempt=2: simplified prompt without accessories
    attempt=3: attempt 1 with stricter negative prompt
    """
    species = metadata.get("species", "rabbit")
    fur_color = metadata.get("fur_color", "brown")
    eye_color = metadata.get("eye_color", "brown")
    hairstyle = metadata.get("hairstyle", "short")
    accessories: list[str] = metadata.get("accessories", [])
    top_color = metadata.get("clothes_top_color", "blue")
    bottom_color = metadata.get("clothes_bottom_color", "white")
    personality = metadata.get("personality", "friendly and curious")
    appearance_summary = metadata.get("appearance_summary", "")

    accessories_part = f", accessories: {', '.join(accessories)}" if accessories else ""

    if attempt == 2:
        prompt_text = _SIMPLIFIED_TEMPLATE.format(
            prefix=_GLOBAL_PREFIX,
            species=species,
            fur_color=fur_color,
            eye_color=eye_color,
            hairstyle=hairstyle,
            top_color=top_color,
            bottom_color=bottom_color,
            negative=_GLOBAL_NEGATIVE,
        )
    elif attempt == 3:
        prompt_text = _CHARACTER_TEMPLATE.format(
            prefix=_GLOBAL_PREFIX,
            species=species,
            fur_color=fur_color,
            eye_color=eye_color,
            hairstyle=hairstyle,
            accessories_part=accessories_part,
            top_color=top_color,
            bottom_color=bottom_color,
            personality=personality,
            appearance_summary=appearance_summary,
            negative=_GLOBAL_NEGATIVE + _STRICT_EXTRA_NEGATIVE,
        )
    else:
        prompt_text = _CHARACTER_TEMPLATE.format(
            prefix=_GLOBAL_PREFIX,
            species=species,
            fur_color=fur_color,
            eye_color=eye_color,
            hairstyle=hairstyle,
            accessories_part=accessories_part,
            top_color=top_color,
            bottom_color=bottom_color,
            personality=personality,
            appearance_summary=appearance_summary,
            negative=_GLOBAL_NEGATIVE,
        )

    return VersionedPrompt(
        text=prompt_text, prompt_version=PROMPT_VERSION, attempt=attempt
    )
