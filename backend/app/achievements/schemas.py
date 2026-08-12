from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    key: str
    category: str
    title: str
    description: str
    hidden: bool
    icon_path: str
    unlocked_at: datetime | None = None


class PlayerAchievementResponse(AchievementResponse):
    avatar_id: uuid.UUID | None = None


class AchievementListResponse(BaseModel):
    achievements: list[AchievementResponse]


class PlayerAchievementListResponse(BaseModel):
    account_id: uuid.UUID
    achievements: list[PlayerAchievementResponse]
