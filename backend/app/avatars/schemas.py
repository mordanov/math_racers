from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

_HEX_COLOUR_PATTERN = r"^#[0-9A-Fa-f]{6}$"
_SPECIES = ("fox", "rabbit", "bear", "cat", "mouse", "panda")
_DEFAULT_FUR = "#D2691E"
_DEFAULT_EYE = "#4B0082"
_DEFAULT_TOP = "#4169E1"
_DEFAULT_BOTTOM = "#FFFFFF"
_DEFAULT_HAIRSTYLE = "short"


class CreateAvatarRequest(BaseModel):
    species: str
    fur_color: str = _DEFAULT_FUR
    eye_color: str = _DEFAULT_EYE
    hairstyle: str = _DEFAULT_HAIRSTYLE
    accessories: list[str] = Field(default_factory=list, max_length=10)
    clothes_top_color: str = _DEFAULT_TOP
    clothes_bottom_color: str = _DEFAULT_BOTTOM

    @field_validator("species")
    @classmethod
    def validate_species(cls, v: str) -> str:
        if v not in _SPECIES:
            raise ValueError(f"species must be one of {_SPECIES}")
        return v

    @field_validator("fur_color", "eye_color", "clothes_top_color", "clothes_bottom_color")
    @classmethod
    def validate_hex_colour(cls, v: str) -> str:
        import re

        if not re.match(_HEX_COLOUR_PATTERN, v):
            raise ValueError("must be a valid hex colour in #RRGGBB format")
        return v

    @field_validator("hairstyle")
    @classmethod
    def validate_hairstyle(cls, v: str) -> str:
        if not v or len(v) > 50:
            raise ValueError("hairstyle must be 1–50 characters")
        return v

    @field_validator("accessories")
    @classmethod
    def validate_accessories(cls, v: list[str]) -> list[str]:
        for item in v:
            if len(item) > 50:
                raise ValueError("each accessory name must be ≤50 characters")
        return v


class AvatarCreationResponse(BaseModel):
    avatar_id: uuid.UUID
    job_id: uuid.UUID
    status: str


class JobStatusResponse(BaseModel):
    job_id: uuid.UUID
    avatar_id: uuid.UUID
    status: str
    attempt: int
    error: str | None
    created_at: datetime
    completed_at: datetime | None


class PortraitSummary(BaseModel):
    id: uuid.UUID
    version: int
    prompt_version: str
    model_version: str
    full_url: str
    medium_url: str
    small_url: str
    thumb_url: str
    created_at: datetime


class AvatarListItem(BaseModel):
    avatar_id: uuid.UUID
    name: str | None
    species: str
    status: str
    is_favourite: bool
    portrait: PortraitSummary | None
    created_at: datetime


class AvatarDetailResponse(BaseModel):
    avatar_id: uuid.UUID
    species: str
    fur_color: str
    eye_color: str
    hairstyle: str
    accessories: list[str]
    clothes_top_color: str
    clothes_bottom_color: str
    name: str | None
    personality: str | None
    biography: str | None
    appearance_summary: str | None
    favorite_subject: str | None
    running_style: str | None
    status: str
    is_favourite: bool
    active_portrait_id: uuid.UUID | None
    portrait: PortraitSummary | None
    portrait_history: list[PortraitSummary]
    created_at: datetime


class PatchAvatarRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    is_favourite: bool | None = None
    active_portrait_id: uuid.UUID | None = None
