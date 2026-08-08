import asyncio
import logging
import time

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from infrastructure.config import get_config

router = APIRouter()
logger = logging.getLogger(__name__)

# Module-level singletons so health checks don't pay engine/client startup cost per request.
_db_engine = None
_redis_client = None
_http_client = None


def _get_db_engine():
    global _db_engine
    if _db_engine is None:
        cfg = get_config()
        _db_engine = create_async_engine(
            cfg.DATABASE_URL.get_secret_value(),
            pool_size=2,
            max_overflow=0,
        )
    return _db_engine


def _get_redis_client():
    global _redis_client
    if _redis_client is None:
        cfg = get_config()
        _redis_client = aioredis.from_url(cfg.REDIS_URL, socket_timeout=2)
    return _redis_client


def _get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=0.5, read=0.5, write=0.5, pool=0.5)
        )
    return _http_client


async def _check_database() -> str:
    try:
        async with _get_db_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        logger.warning("Database health check failed")
        return "unavailable"


async def _check_redis() -> str:
    try:
        await _get_redis_client().ping()
        return "ok"
    except Exception:
        logger.warning("Redis health check failed")
        return "unavailable"


async def _check_storage() -> str:
    cfg = get_config()
    endpoint = cfg.STORAGE_ENDPOINT
    # Skip probe when endpoint is unconfigured (placeholder value).
    if not endpoint or "CHANGE_ME" in endpoint:
        return "unavailable"
    try:
        resp = await asyncio.wait_for(
            _get_http_client().get(endpoint),
            timeout=0.8,
        )
        return "ok" if resp.status_code < 500 else "unavailable"
    except asyncio.TimeoutError:
        logger.warning("Storage health check timed out")
        return "unavailable"
    except Exception:
        logger.warning("Storage health check failed")
        return "unavailable"


@router.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    start = time.monotonic()
    cfg = get_config()

    db_status, redis_status, storage_status = await asyncio.gather(
        _check_database(),
        _check_redis(),
        _check_storage(),
    )

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
