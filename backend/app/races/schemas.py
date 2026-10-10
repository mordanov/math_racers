from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.achievements.schemas import AchievementResponse
from app.progression.schemas import ProgressionResponse


class ParticipantSummaryRequest(BaseModel):
    avatar_id: str
    position: Annotated[int, Field(ge=1, le=5)] | None = None
    problems_correct: Annotated[int, Field(ge=0)]
    longest_streak: Annotated[int, Field(ge=0)]
    average_response_ms: Annotated[int, Field(ge=0)]
    total_distance: Annotated[int, Field(ge=0)]
    xp_earned: Annotated[int, Field(ge=0)]


class OperationAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["addition", "subtraction", "multiplication", "division"]
    is_correct: bool
    response_time_ms: Annotated[int, Field(ge=0)]
    submitted_answer: str | None = None


class RaceResultAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["addition", "subtraction", "multiplication", "division"]
    answer: Annotated[str, Field(max_length=32)]
    response_time_ms: Annotated[int, Field(ge=0)] | None = None


class CustomTierConfigRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operations: Annotated[
        list[Literal["addition", "subtraction", "multiplication", "division"]],
        Field(min_length=1, max_length=4),
    ]
    min_operand: Annotated[int, Field(ge=1, le=100)]
    max_operand: Annotated[int, Field(ge=1, le=100)]

    @model_validator(mode="after")
    def validate_settings(self) -> CustomTierConfigRequest:
        if self.min_operand > self.max_operand:
            raise ValueError("min_operand cannot be greater than max_operand.")
        if len(self.operations) != len(set(self.operations)):
            raise ValueError("operations must not contain duplicates.")
        return self


class RaceSummaryRequest(BaseModel):
    human_avatar_id: str
    race_id: uuid.UUID
    child_profile_id: uuid.UUID | None = None
    idempotency_key: uuid.UUID | None = None
    seed: str
    difficulty_tier: Annotated[int, Field(ge=1, le=6)]
    mode: Literal["quick", "championship", "duel", "training"]
    started_at: datetime
    completed_at: datetime
    participants: Annotated[list[ParticipantSummaryRequest], Field(min_length=1, max_length=5)]
    answers: list[OperationAnswerRequest] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_positions(self) -> RaceSummaryRequest:
        for p in self.participants:
            if self.mode == "training":
                if p.position is not None:
                    raise ValueError("position must be null for training mode")
            else:
                if p.position is None:
                    raise ValueError("position is required for non-training modes")
        return self


class RaceSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["quick", "championship", "duel", "training"]
    difficulty_tier: Annotated[int, Field(ge=1, le=6)]
    avatar_id: uuid.UUID
    opponent_count: Annotated[int, Field(ge=0, le=4)]
    championship_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_training_opponents(self) -> RaceSessionRequest:
        if self.mode == "training" and self.opponent_count != 0:
            raise ValueError("Training sessions cannot have opponents.")
        if (self.mode == "championship") != (self.championship_id is not None):
            raise ValueError("Championship sessions require a championship ID.")
        return self


class RaceSessionResponse(BaseModel):
    race_id: uuid.UUID
    seed: int


class RaceResultParticipantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    avatar_id: str
    position: Annotated[int, Field(ge=1, le=5)] | None = None


class RaceResultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: uuid.UUID
    human_avatar_id: str
    participants: Annotated[list[RaceResultParticipantRequest], Field(min_length=1, max_length=5)]
    answers: list[RaceResultAnswerRequest] = Field(default_factory=list)


class RaceAnswerSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_index: Annotated[int, Field(ge=0)]
    operation: Literal["addition", "subtraction", "multiplication", "division"]
    answer: Annotated[str, Field(max_length=32)]


class RaceAnswerSubmitResponse(BaseModel):
    answer_index: int
    is_correct: bool
    response_time_ms: int


class RaceSummaryResponse(BaseModel):
    race_id: uuid.UUID
    created_at: datetime
    progression: ProgressionResponse | None = None
    new_achievements: list[AchievementResponse] = []
