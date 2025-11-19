from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health", summary="Gateway health check")
async def health(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.env,
    }


@router.get("/version", summary="Gateway version info")
async def version(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    return {
        "service": "public-api",
        "appVersion": settings.app_version,
        "commit": settings.commit,
        "buildTime": settings.build_time,
        "environment": settings.env,
    }
