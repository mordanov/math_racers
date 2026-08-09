from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from infrastructure.config import get_config

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        cfg = get_config()
        _engine = create_async_engine(
            cfg.DATABASE_URL.get_secret_value(),
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    return _engine
