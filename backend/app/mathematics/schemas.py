from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import BaseModel, Field


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
