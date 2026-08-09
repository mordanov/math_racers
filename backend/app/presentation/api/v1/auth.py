from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import Response as PlainResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.domain_service import AccountDomainService
from app.accounts.models import Account
from app.accounts.repository import (
    SQLAlchemyAccountRepository,
    SQLAlchemyRefreshTokenRepository,
)
from app.accounts.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.presentation.api.middleware.auth import get_current_account
from app.shared.exceptions import PermissionError
from application.login import LoginUseCase
from application.logout import LogoutUseCase
from application.refresh_token import RefreshTokenUseCase
from application.register_account import RegisterAccountUseCase
from infrastructure.config import Config, get_config
from infrastructure.database.session import get_session

_REFRESH_COOKIE = "refresh_token"
_REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    account_repo = SQLAlchemyAccountRepository(session)
    use_case = RegisterAccountUseCase(account_repo, AccountDomainService())
    await use_case.execute(body.email, body.password)
    return {"message": "Registration successful. Awaiting administrator approval."}


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    settings: Config = Depends(get_config),
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    account_repo = SQLAlchemyAccountRepository(session)
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(session)
    use_case = LoginUseCase(account_repo, refresh_token_repo, AccountDomainService())

    access_token, raw_refresh = await use_case.execute(body.email, body.password, settings)

    ttl_seconds = settings.JWT_REFRESH_TTL_DAYS * 86400
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=raw_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        path=_REFRESH_COOKIE_PATH,
        max_age=ttl_seconds,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    settings: Config = Depends(get_config),
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    raw_refresh = request.cookies.get(_REFRESH_COOKIE)
    if not raw_refresh:
        raise PermissionError("INVALID_REFRESH_TOKEN", "Refresh token cookie missing.")

    account_repo = SQLAlchemyAccountRepository(session)
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(session)
    use_case = RefreshTokenUseCase(account_repo, refresh_token_repo, AccountDomainService())

    new_access, new_raw = await use_case.execute(raw_refresh, settings)

    ttl_seconds = settings.JWT_REFRESH_TTL_DAYS * 86400
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=new_raw,
        httponly=True,
        secure=True,
        samesite="lax",
        path=_REFRESH_COOKIE_PATH,
        max_age=ttl_seconds,
    )
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=204, response_class=PlainResponse)
async def logout(
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> PlainResponse:
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(session)
    use_case = LogoutUseCase(refresh_token_repo)
    await use_case.execute(account.id)

    response = PlainResponse(status_code=204)
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        path=_REFRESH_COOKIE_PATH,
        max_age=0,
    )
    return response
