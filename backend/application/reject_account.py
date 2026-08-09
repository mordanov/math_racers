from __future__ import annotations

import uuid

from app.accounts.models import Account, ApprovalStatus
from app.accounts.repository import AccountRepository
from app.shared.exceptions import NotFoundError, ValidationError


class RejectAccountUseCase:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    async def execute(self, account_id: uuid.UUID) -> Account:
        account = await self._account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError("ACCOUNT_NOT_FOUND", "Account not found.")

        if account.approval_status != ApprovalStatus.pending:
            raise ValidationError(
                "INVALID_ACCOUNT_STATE",
                "Only pending accounts can be rejected.",
            )

        account.approval_status = ApprovalStatus.rejected
        return await self._account_repo.save(account)
