import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

# Context variable holding the current request's correlation ID.
# Falls back to nil UUID for non-request-scoped log entries.
_NIL_UUID = "00000000-0000-0000-0000-000000000000"
request_id_var: ContextVar[str] = ContextVar("request_id", default=_NIL_UUID)

_REDACT_PATTERN = re.compile(r"(password|secret|token|key)", re.IGNORECASE)


def _redact(obj: Any, depth: int = 0) -> Any:
    """Recursively redact sensitive keys from a dict up to depth 5."""
    if depth > 5:
        return obj
    if isinstance(obj, dict):
        return {
            k: "***REDACTED***" if _REDACT_PATTERN.search(str(k)) else _redact(v, depth + 1)
            for k, v in obj.items()
        }
    if isinstance(obj, (list, tuple)):
        return [_redact(i, depth + 1) for i in obj]
    return obj


class StructuredFormatter(logging.Formatter):
    """Emit JSON log entries with all required fields."""

    def __init__(self, service: str) -> None:
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        context = _redact(getattr(record, "context", {}))
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.service,
            "request_id": request_id_var.get(),
            "message": record.getMessage(),
            "context": context,
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def setup_logging(service: str = "backend", level: str = "INFO") -> None:
    """Configure the root logger with structured JSON output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter(service=service))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_request_id(rid: str | UUID) -> None:
    request_id_var.set(str(rid))
