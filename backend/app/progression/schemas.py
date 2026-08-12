from __future__ import annotations

from pydantic import BaseModel


class LevelUpEvent(BaseModel):
    previous_level: int
    new_level: int
    total_xp: int


class ProgressionResponse(BaseModel):
    total_xp: int
    current_level: int
    xp_to_next_level: int
    xp_earned_this_race: int | None = None
    level_up: LevelUpEvent | None = None
