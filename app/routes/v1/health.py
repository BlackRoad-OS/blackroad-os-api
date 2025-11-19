from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health", summary="Versioned health check")
async def health(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.env,
        "upstreams": {
            "coreConfigured": settings.core_configured,
            "agentsConfigured": settings.agents_configured,
        },
    }
