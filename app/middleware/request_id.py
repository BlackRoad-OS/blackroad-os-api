"""Request ID middleware for tracing and observability."""

from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next):
        # Use existing request ID from header if provided, otherwise generate one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
