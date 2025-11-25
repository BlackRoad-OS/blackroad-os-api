"""Error handling middleware for consistent error responses."""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.errors import UpstreamError, build_error_response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware that catches exceptions and returns consistent error responses."""

    async def dispatch(self, request: Request, call_next):
        request_id = getattr(request.state, "request_id", None)

        try:
            return await call_next(request)
        except UpstreamError as exc:
            # Log upstream errors without exposing internal details
            logger.warning(
                "Upstream error from %s: %s",
                exc.source,
                exc.detail,
                extra={"request_id": request_id, "source": exc.source},
            )
            payload = build_error_response(
                code="UPSTREAM_ERROR",
                message=str(exc.detail),
                request_id=request_id,
                details=exc.details,
            )
            return JSONResponse(status_code=exc.status_code, content=payload)
        except Exception as exc:
            # Log unexpected errors without exposing stack traces to clients
            logger.exception(
                "Unexpected error: %s",
                str(exc),
                extra={"request_id": request_id},
            )
            payload = build_error_response(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                request_id=request_id,
            )
            return JSONResponse(status_code=500, content=payload)
