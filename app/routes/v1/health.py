from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.routes.root import build_health_payload

router = APIRouter()


@router.get("/health", summary="Versioned health check")
async def health(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    return build_health_payload(settings)
