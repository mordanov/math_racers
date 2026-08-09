from __future__ import annotations

import uuid

from app.accounts.repository import RefreshTokenRepository


class LogoutUseCase:
    def __init__(self, refresh_token_repo: RefreshTokenRepository) -> None:
        self._refresh_token_repo = refresh_token_repo

    async def execute(self, account_id: uuid.UUID) -> None:
        await self._refresh_token_repo.revoke_all_for_account(account_id)
