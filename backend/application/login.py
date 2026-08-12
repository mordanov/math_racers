from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import ApprovalStatus, RefreshToken
from app.accounts.repository import AccountRepository, RefreshTokenRepository
from app.shared.exceptions import PermissionError
from infrastructure.config import Config


class LoginUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        refresh_token_repo: RefreshTokenRepository,
        domain_service: AccountDomainService,
    ) -> None:
        self._account_repo = account_repo
        self._refresh_token_repo = refresh_token_repo
        self._domain_service = domain_service

    async def execute(
        self, email: str, password: str, settings: Config
    ) -> tuple[str, str]:
        normalised_email = email.strip().lower()

        account = await self._account_repo.get_by_email(normalised_email)
        if account is None:
            raise PermissionError("INVALID_CREDENTIALS", "Invalid email or password.")

        if not self._domain_service.verify_password(password, account.password_hash):
            raise PermissionError("INVALID_CREDENTIALS", "Invalid email or password.")

        if account.approval_status == ApprovalStatus.pending:
            raise PermissionError(
                "ACCOUNT_PENDING",
                "Your account is pending administrator approval.",
            )
        if account.approval_status == ApprovalStatus.rejected:
            raise PermissionError(
                "ACCOUNT_REJECTED",
                "Your account has been rejected.",
            )

        access_token = self._domain_service.create_access_token(
            account.id, account.role, settings
        )
        raw_refresh, token_hash = self._domain_service.generate_refresh_token()

        refresh_token = RefreshToken(
            account_id=account.id,
            token_hash=token_hash,
            expires_at=datetime.now(tz=UTC)
            + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        )
        await self._refresh_token_repo.save(refresh_token)

        return access_token, raw_refresh
