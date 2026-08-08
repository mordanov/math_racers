import logging
import subprocess
import sys

from fastapi import FastAPI

from app.presentation.api.middleware.correlation_id import CorrelationIdMiddleware
from app.presentation.api.v1.health import router as health_router
from infrastructure.config import get_config
from infrastructure.logging import setup_logging

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    """Apply pending migrations. Abort startup on failure."""
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

    @app.on_event("startup")
    async def startup() -> None:
        _run_migrations()
        from infrastructure.queue.recovery import recover_pending_jobs

        await recover_pending_jobs()

    return app


app = create_app()
