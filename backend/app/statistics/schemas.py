from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PlayerStatsResponse(BaseModel):
    player_id: str
    total_races: int
    total_problems_solved: int
    correct_answers: int
    accuracy_all_time: float | None
    avg_response_ms: int | None
    favourite_operation: str | None
    best_streak: int
    updated_at: datetime


class AvatarStatsResponse(BaseModel):
    avatar_id: str
    player_id: str
    total_races: int
    wins: int
    podiums: int
    best_streak: int
    last_race_at: datetime


class RaceSessionResponse(BaseModel):
    id: str
    avatar_id: str
    mode: str
    finishing_position: int | None
    problems_solved: int
    correct_answers: int
    mistakes: int
    difficulty_tier: int
    xp_earned: int
    avg_response_ms: int
    longest_streak: int
    started_at: datetime
    finished_at: datetime


class HistoryResponse(BaseModel):
    results: list[RaceSessionResponse]
    page: int
    total_pages: int
    total_records: int


class WeeklySummaryResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    problems_solved: int
    correct_answers: int
    accuracy: float | None
    avg_response_ms: int | None
    strongest_operation: str | None
    weakest_operation: str | None
    races_completed: int
    xp_earned: int


class PersonalRecordsResponse(BaseModel):
    best_streak: int
    best_race_accuracy: float | None
    fastest_avg_response_ms: int | None
    total_races: int
