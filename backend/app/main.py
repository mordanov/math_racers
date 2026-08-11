import logging
import subprocess
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.presentation.api.middleware.correlation_id import CorrelationIdMiddleware
from app.presentation.api.v1.health import router as health_router
from app.shared.exceptions import (
    ConflictError,
    DomainError,
    LastAdministratorError,
    NotFoundError,
    PermissionError,
    UnauthorizedError,
    ValidationError,
)
from infrastructure.config import get_config
from infrastructure.logging import request_id_var, setup_logging

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(
                "Database migration failed — aborting startup",
                extra={"context": {"stderr": result.stderr.strip()}},
            )
            sys.exit(1)
        logger.info(
            "Database migrations applied",
            extra={"context": {"output": result.stdout.strip() or "already at head"}},
        )
    except Exception as exc:
        logger.error(
            "Failed to run migrations",
            extra={"context": {"error": str(exc)}},
        )
        sys.exit(1)


async def _seed_default_admin() -> None:
    cfg = get_config()
    try:
        admin_email = cfg.ADMIN_EMAIL.get_secret_value().strip().lower()
        admin_password = cfg.ADMIN_PASSWORD.get_secret_value()
    except Exception:
        logger.error("ADMIN_EMAIL or ADMIN_PASSWORD not configured — aborting startup")
        sys.exit(1)

    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.accounts.domain_service import AccountDomainService
    from app.accounts.models import Account, AccountRole, ApprovalStatus
    from app.accounts.repository import SQLAlchemyAccountRepository
    from infrastructure.database.engine import get_engine

    engine = get_engine()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with session_factory() as session:
        async with session.begin():
            repo = SQLAlchemyAccountRepository(session)
            count = await repo.count_approved_administrators()
            if count == 0:
                domain_service = AccountDomainService()
                password_hash = domain_service.hash_password(admin_password)
                admin = Account(
                    email=admin_email,
                    password_hash=password_hash,
                    role=AccountRole.administrator,
                    approval_status=ApprovalStatus.approved,
                )
                await repo.save(admin)
                logger.info(
                    "Default administrator account seeded",
                    extra={"context": {"email": admin_email}},
                )
            else:
                logger.info(
                    "Administrator account(s) already exist — skipping seed",
                    extra={"context": {"count": count}},
                )


_DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    ValidationError: 422,
    NotFoundError: 404,
    ConflictError: 409,
    UnauthorizedError: 401,
    PermissionError: 403,
    LastAdministratorError: 400,
}


def _domain_error_status(exc: DomainError) -> int:
    for cls, status in _DOMAIN_ERROR_STATUS.items():
        if isinstance(exc, cls):
            return status
    return 500


def create_app() -> FastAPI:
    cfg = get_config()
    setup_logging(service="backend", level=cfg.LOG_LEVEL)

    app = FastAPI(
        title="Math Racers API",
        version=cfg.VERSION,
        docs_url=None if cfg.ENVIRONMENT.value == "production" else "/docs",
        redoc_url=None if cfg.ENVIRONMENT.value == "production" else "/redoc",
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(health_router)

    from app.avatars.presentation.api.v1.avatars import router as avatars_router
    from app.presentation.api.v1.admin import router as admin_router
    from app.presentation.api.v1.auth import router as auth_router
    from app.presentation.api.v1.championships import router as championships_router
    from app.presentation.api.v1.difficulty import router as difficulty_router
    from app.presentation.api.v1.opponents import router as opponents_router
    from app.presentation.api.v1.problems import router as problems_router
    from app.races.presentation.api.v1.races import router as races_router

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(problems_router)
    app.include_router(difficulty_router)
    app.include_router(opponents_router)
    app.include_router(races_router)
    app.include_router(championships_router)
    app.include_router(avatars_router)

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=_domain_error_status(exc),
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "request_id": request_id_var.get(),
            },
        )

    @app.on_event("startup")
    async def startup() -> None:
        _run_migrations()
        await _seed_default_admin()
        from infrastructure.queue.recovery import recover_pending_jobs

        await recover_pending_jobs()

    return app


app = create_app()
