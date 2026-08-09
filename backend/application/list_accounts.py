from __future__ import annotations

from app.accounts.models import Account
from app.accounts.repository import AccountRepository


class ListAccountsUseCase:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    async def execute(
        self,
        status: str | None,
        role: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Account], int]:
        return await self._account_repo.list_by_status(status, role, limit, offset)
