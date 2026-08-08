import logging
import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from infrastructure.config import get_config

router = APIRouter()
logger = logging.getLogger(__name__)


async def _check_database() -> str:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    cfg = get_config()
    try:
        engine = create_async_engine(
            cfg.DATABASE_URL.get_secret_value(),
            pool_size=1,
            max_overflow=0,
        )
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return "ok"
    except Exception:
        logger.warning("Database health check failed")
        return "unavailable"


async def _check_redis() -> str:
    import redis.asyncio as aioredis

    cfg = get_config()
    try:
        client = aioredis.from_url(cfg.REDIS_URL)
        await client.ping()
        await client.aclose()
        return "ok"
    except Exception:
        logger.warning("Redis health check failed")
        return "unavailable"


async def _check_storage() -> str:
    import httpx

    cfg = get_config()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(cfg.STORAGE_ENDPOINT)
            return "ok" if resp.status_code < 500 else "unavailable"
    except Exception:
        logger.warning("Storage health check failed")
        return "unavailable"


@router.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    start = time.monotonic()
    cfg = get_config()

    db_status = await _check_database()
    redis_status = await _check_redis()
    storage_status = await _check_storage()

    checks = {
        "database": db_status,
        "redis": redis_status,
        "storage": storage_status,
    }

    if db_status == "unavailable":
        overall = "unavailable"
        http_status = 503
    elif "unavailable" in checks.values():
        overall = "degraded"
        http_status = 200
    else:
        overall = "ok"
        http_status = 200

    elapsed_ms = (time.monotonic() - start) * 1000
    if elapsed_ms > 100:
        logger.warning(
            "Health check exceeded 100ms target",
            extra={"context": {"elapsed_ms": round(elapsed_ms, 1)}},
        )

    return JSONResponse(
        status_code=http_status,
        content={
            "status": overall,
            "version": cfg.VERSION,
            "checks": checks,
        },
    )
