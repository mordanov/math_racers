import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from infrastructure.logging import set_request_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Generate a UUID correlation ID per request and inject it into the log context."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        raw_id = request.headers.get("X-Request-ID")
        try:
            request_id = str(uuid.UUID(raw_id)) if raw_id else str(uuid.uuid4())
        except ValueError:
            request_id = str(uuid.uuid4())

        set_request_id(request_id)
        request.state.request_id = request_id

        response: Response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Request-ID"] = request_id
        return response
