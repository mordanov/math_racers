from __future__ import annotations

import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class ProblemResponse(BaseModel):
    id: uuid.UUID
    operation: str
    operand_a: int
    operand_b: int
    answer: int
    tier: int
    seed: int


class ProblemSetResponse(BaseModel):
    seed: int
    tier: int
    count: int
    problems: list[ProblemResponse]


class DifficultyResponse(BaseModel):
    player_id: uuid.UUID
    current_tier: int
    parent_override: int | None
    effective_tier: int


class DifficultyPatchRequest(BaseModel):
    parent_override: Annotated[int | None, Field(ge=1, le=6)] = None


class Tier6Settings(BaseModel):
    operations: Annotated[
        list[Literal["addition", "subtraction", "multiplication", "division"]],
        Field(min_length=1, max_length=4),
    ]
    min_operand: Annotated[int, Field(ge=1, le=100)]
    max_operand: Annotated[int, Field(ge=1, le=100)]

    @model_validator(mode="after")
    def validate_settings(self) -> Tier6Settings:
        if self.min_operand > self.max_operand:
            raise ValueError("min_operand cannot be greater than max_operand.")
        if len(self.operations) != len(set(self.operations)):
            raise ValueError("operations must not contain duplicates.")
        return self


class Tier6SettingsResponse(BaseModel):
    custom_tier_config: Tier6Settings | None


class Tier6SettingsPatchRequest(BaseModel):
    custom_tier_config: Tier6Settings
