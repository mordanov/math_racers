from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ParticipantSummaryRequest(BaseModel):
    avatar_id: str
    position: Annotated[int, Field(ge=1, le=5)]
    problems_correct: Annotated[int, Field(ge=0, le=8)]
    average_response_ms: Annotated[int, Field(ge=0)]
    total_distance: Annotated[int, Field(ge=0, le=144)]
    xp_earned: Annotated[int, Field(ge=0)]


class RaceSummaryRequest(BaseModel):
    race_id: uuid.UUID
    seed: str
    difficulty_tier: Annotated[int, Field(ge=1, le=6)]
    mode: Literal["quick", "championship", "duel", "training"]
    started_at: datetime
    completed_at: datetime
    participants: Annotated[list[ParticipantSummaryRequest], Field(min_length=1, max_length=5)]


class RaceSummaryResponse(BaseModel):
    race_id: uuid.UUID
    created_at: datetime
