from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.clients.upstream import UpstreamClient, get_agents_client
from app.config import Settings, get_settings
from app.middleware.auth import api_key_auth

router = APIRouter(dependencies=[Depends(api_key_auth)])


@router.get("/agents/health", summary="Proxy agents health", status_code=status.HTTP_200_OK)
async def agents_health(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    agents_client: UpstreamClient = get_agents_client(settings.agents_api_url)
    return await agents_client.request("GET", "/health")
