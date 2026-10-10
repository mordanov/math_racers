from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from infrastructure.config import get_config

_STATE_CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _allowed_origins(request: Request) -> set[str]:
    configured = get_config().CSRF_ALLOWED_ORIGINS
    if configured.strip():
        return {origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()}
    return {f"{request.url.scheme}://{request.url.netloc}"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method in _STATE_CHANGING_METHODS:
            origin = request.headers.get("origin")
            allowed = _allowed_origins(request)
            normalized_origin = origin.rstrip("/") if origin else None
            if normalized_origin not in allowed:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error_code": "CSRF_ORIGIN_REJECTED",
                        "message": "The request origin is not allowed.",
                    },
                )

            cookie_token = request.cookies.get("csrf_token")
            header_token = request.headers.get("X-CSRF-Token")
            if (
                not cookie_token
                or not header_token
                or not secrets.compare_digest(cookie_token, header_token)
            ):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error_code": "CSRF_TOKEN_REJECTED",
                        "message": "A valid CSRF token and allowed origin are required.",
                    },
                )

        return await call_next(request)
