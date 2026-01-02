"""Application entrypoint for blackroad-os-api."""

import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.generated.router import router as generated_router
from app.middleware.response_headers import ResponseHeaderMiddleware
from app.rate_limiting import limiter


app = FastAPI(
    title="BlackRoad OS Public API",
    description="Public-facing gateway for BlackRoad services",
    version=__version__,
)

app.state.limiter = limiter
app.state.start_time = time.time()

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ResponseHeaderMiddleware)

app.include_router(generated_router)


@app.get("/", include_in_schema=False)
async def index():
    return {"message": "BlackRoad public API gateway", "docs": "/docs"}


@app.get("/health", include_in_schema=False)
async def health():
    """Liveness check - returns 200 if service is running."""
    uptime = time.time() - app.state.start_time
    return {
        "status": "ok",
        "uptime": round(uptime, 2),
    }


@app.get("/ready", include_in_schema=False)
async def ready():
    """Readiness check - safe to hook into load balancers."""
    return {
        "ready": True,
        "service": "blackroad-os-api",
    }


@app.get("/version", include_in_schema=False)
async def version():
    """Return service version, commit, and environment info."""
    return {
        "service": "blackroad-os-api",
        "version": os.getenv("BR_OS_API_VERSION", __version__),
        "commit": os.getenv("BR_OS_API_COMMIT", os.getenv("GIT_COMMIT", "UNKNOWN")),
        "env": os.getenv("BR_OS_ENV", os.getenv("NODE_ENV", "local")),
    }
