from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


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
