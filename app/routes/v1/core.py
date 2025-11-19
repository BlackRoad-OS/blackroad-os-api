from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.clients.core_client import build_core_client
from app.config import Settings, get_settings
router = APIRouter()


@router.get("/core/ping", summary="Proxy core ping", status_code=status.HTTP_200_OK)
async def core_ping(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    core_client = build_core_client(settings)
    return await core_client.request("GET", "/ping")
