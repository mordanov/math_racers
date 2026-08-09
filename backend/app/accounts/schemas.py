from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 128:
            raise ValueError("password must be between 8 and 128 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    approval_status: str
    created_at: datetime
    approved_at: datetime | None
    approved_by: uuid.UUID | None

    model_config = {"from_attributes": True}
