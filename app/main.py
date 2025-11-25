"""Application entrypoint for blackroad-os-api."""

import pathlib
import time
from datetime import datetime, timezone

import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.config import get_settings
from app.core.settings import settings as core_settings
from app.generated import models  # noqa: F401
from app.generated.router import router as generated_router
from app.middleware.errors import ErrorHandlerMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.response_headers import ResponseHeaderMiddleware
from app.rate_limiting import RateLimitExceeded as RateLimitExceededType, limiter

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
OPENAPI_PATH = BASE_DIR / "openapi.yaml"

# Track start time for uptime calculation
_start_time = time.monotonic()


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    from app.errors import build_error_response

    payload = build_error_response(
        code="RATE_LIMIT_EXCEEDED",
        message=str(exc.detail) if getattr(exc, "detail", None) else "Too many requests",
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(status_code=429, content=payload)


app = FastAPI(
    title="BlackRoad OS Public API",
    description="Public-facing gateway for BlackRoad services",
    version=__version__,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceededType, rate_limit_handler)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(ResponseHeaderMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

app.include_router(generated_router)

# retain original generator to avoid recursion when overriding
original_openapi = app.openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    if OPENAPI_PATH.exists():
        with OPENAPI_PATH.open("r", encoding="utf-8") as handle:
            schema = yaml.safe_load(handle)
            app.openapi_schema = schema
            return app.openapi_schema
    return original_openapi()


app.openapi = custom_openapi


@app.get("/", include_in_schema=False)
async def index():
    return {"message": "BlackRoad public API gateway", "docs": "/docs"}


# --- Standard Infrastructure Endpoints (root level) ---
# These endpoints follow BlackRoad OS service conventions

@app.get("/health", include_in_schema=False)
def health():
    """Lightweight liveness check - returns 200 if service is running."""
    uptime = max(time.monotonic() - _start_time, 0.0)
    return {"status": "ok", "uptime": round(uptime, 3)}


@app.get("/ready", include_in_schema=False)
def ready():
    """Readiness check for load balancers."""
    return {
        "ready": True,
        "service": "blackroad-os-api",
    }


@app.get("/version", include_in_schema=False)
def version():
    """Service version, commit, and environment info."""
    return {
        "version": core_settings.version,
        "commit": core_settings.git_sha,
    }
