from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class CreateChampionshipRequest(BaseModel):
    total_races: Annotated[int, Field(ge=3, le=7)]


class RaceParticipantEntry(BaseModel):
    avatar_id: str
    is_player: bool
    finishing_position: Annotated[int, Field(ge=1, le=5)]


class RecordRaceRequest(BaseModel):
    race_index: Annotated[int, Field(ge=0)]
    participants: Annotated[list[RaceParticipantEntry], Field(min_length=1, max_length=5)]


class StandingEntry(BaseModel):
    avatar_id: str
    is_player: bool
    points: int
    podiums: int
    position: int


class ChampionshipResponse(BaseModel):
    championship_id: uuid.UUID
    total_races: int
    races_completed: int
    status: str
    standings: list[StandingEntry]
    created_at: datetime | None = None
