from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.clients.agents_client import build_agents_client
from app.config import Settings, get_settings
router = APIRouter()


@router.get("/agents/ping", summary="Proxy agents ping", status_code=status.HTTP_200_OK)
async def agents_ping(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    agents_client = build_agents_client(settings)
    return await agents_client.request("GET", "/ping")
