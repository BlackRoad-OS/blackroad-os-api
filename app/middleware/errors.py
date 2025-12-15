from __future__ import annotations

from typing import Any, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.errors import UpstreamError, build_error_response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request.scope.setdefault("headers", [])
        request_id = request.headers.get("X-Request-ID")
        try:
            return await call_next(request)
        except UpstreamError as exc:  # pragma: no cover - exercised via tests
            details: Dict[str, Any] = {"source": exc.source, **(exc.details or {})}
            content = build_error_response(
                code="UPSTREAM_ERROR",
                message=str(exc.detail),
                request_id=request_id,
                details=details,
            )
            return JSONResponse(status_code=exc.status_code, content=content)
        except Exception as exc:  # pragma: no cover - exercised via tests
            content = build_error_response(
                code="INTERNAL_ERROR",
                message=str(exc) or "Unexpected internal error",
                request_id=request_id,
            )
            return JSONResponse(status_code=500, content=content)
