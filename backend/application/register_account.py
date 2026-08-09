from __future__ import annotations

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.accounts.repository import AccountRepository
from app.shared.exceptions import ConflictError


class RegisterAccountUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        domain_service: AccountDomainService,
    ) -> None:
        self._account_repo = account_repo
        self._domain_service = domain_service

    async def execute(self, email: str, password: str) -> None:
        normalised_email = email.strip().lower()

        existing = await self._account_repo.get_by_email(normalised_email)
        if existing is not None:
            raise ConflictError("EMAIL_TAKEN", "An account with this email already exists.")

        password_hash = self._domain_service.hash_password(password)
        account = Account(
            email=normalised_email,
            password_hash=password_hash,
            role=AccountRole.parent,
            approval_status=ApprovalStatus.pending,
        )
        await self._account_repo.save(account)
