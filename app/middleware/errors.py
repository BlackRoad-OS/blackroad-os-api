from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.errors import UpstreamError, build_error_response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except UpstreamError as exc:
            payload = build_error_response(
                code="UPSTREAM_ERROR",
                message=exc.detail,
                details={"source": exc.source, **exc.details},
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(status_code=exc.status_code, content=payload)
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else None
            code = detail.get("code") if detail else "BAD_REQUEST"
            message = detail.get("message") if detail else str(exc.detail)
            payload = build_error_response(
                code=code or "BAD_REQUEST",
                message=message or "Request error",
                details=detail.get("details") if detail else None,
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(status_code=exc.status_code, content=payload)
        except Exception as exc:  # pylint: disable=broad-except
            payload = build_error_response(
                code="INTERNAL_ERROR",
                message=str(exc) or "Internal server error",
                details=None,
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
