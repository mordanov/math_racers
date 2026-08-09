from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.shared.exceptions import PermissionError
from infrastructure.config import Config


class AccountDomainService:
    _BCRYPT_WORK_FACTOR = 12
    _ALGORITHM = "HS256"

    def hash_password(self, plain: str) -> str:
        return bcrypt.hashpw(
            plain.encode(), bcrypt.gensalt(self._BCRYPT_WORK_FACTOR)
        ).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def create_access_token(
        self, account_id: uuid.UUID, role: str, settings: Config
    ) -> str:
        now = datetime.now(tz=UTC)
        payload = {
            "sub": str(account_id),
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET.get_secret_value(),
            algorithm=self._ALGORITHM,
        )

    def decode_access_token(self, token: str, settings: Config) -> dict[str, object]:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET.get_secret_value(),
                algorithms=[self._ALGORITHM],
            )
        except jwt.ExpiredSignatureError as exc:
            raise PermissionError("TOKEN_EXPIRED", "Access token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise PermissionError("INVALID_TOKEN", "Access token is invalid.") from exc

    def generate_refresh_token(self) -> tuple[str, str]:
        raw = str(uuid.uuid4())
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        return raw, token_hash
