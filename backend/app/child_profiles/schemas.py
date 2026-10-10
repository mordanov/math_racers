from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChildProfileResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChildProfileListResponse(BaseModel):
    profiles: list[ChildProfileResponse]


class CreateChildProfileRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)


class LegacyRecordAssignment(BaseModel):
    record_type: Literal[
        "avatar",
        "avatar_stats",
        "achievement",
        "race",
        "statistics",
        "xp_event",
        "championship",
        "progression",
    ]
    record_id: uuid.UUID


class LegacyDataAssignmentRequest(BaseModel):
    records: list[LegacyRecordAssignment] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_records(self) -> LegacyDataAssignmentRequest:
        keys = [(record.record_type, record.record_id) for record in self.records]
        if len(keys) != len(set(keys)):
            raise ValueError("A legacy record may only appear once.")
        return self
