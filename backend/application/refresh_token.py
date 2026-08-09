from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import RefreshToken
from app.accounts.repository import AccountRepository, RefreshTokenRepository
from app.shared.exceptions import PermissionError
from infrastructure.config import Config


class RefreshTokenUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        refresh_token_repo: RefreshTokenRepository,
        domain_service: AccountDomainService,
    ) -> None:
        self._account_repo = account_repo
        self._refresh_token_repo = refresh_token_repo
        self._domain_service = domain_service

    async def execute(self, raw_token: str, settings: Config) -> tuple[str, str]:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        stored = await self._refresh_token_repo.get_by_hash(token_hash)
        if stored is None:
            raise PermissionError("INVALID_REFRESH_TOKEN", "Refresh token not found.")

        now = datetime.now(tz=UTC)
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        if expires_at < now:
            raise PermissionError("INVALID_REFRESH_TOKEN", "Refresh token has expired.")

        if stored.revoked_at is not None:
            raise PermissionError("INVALID_REFRESH_TOKEN", "Refresh token has been revoked.")

        account = await self._account_repo.get_by_id(stored.account_id)
        if account is None:
            raise PermissionError("INVALID_REFRESH_TOKEN", "Account not found.")

        raw_new, new_hash = self._domain_service.generate_refresh_token()
        new_token = RefreshToken(
            account_id=account.id,
            token_hash=new_hash,
            expires_at=now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        )
        await self._refresh_token_repo.save(new_token)
        await self._refresh_token_repo.revoke(stored.id, replaced_by_id=new_token.id)

        new_access_token = self._domain_service.create_access_token(
            account.id, account.role, settings
        )
        return new_access_token, raw_new
