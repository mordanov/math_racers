from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PersonalityDefinitionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    accuracy_rate: float = Field(alias="accuracyRate")
    base_response_time_ms: int = Field(alias="baseResponseTimeMs")
    response_time_variance_ms: int = Field(alias="responseTimeVarianceMs")
    speed_profile: str = Field(alias="speedProfile")
    tier_offset: int = Field(alias="tierOffset")
