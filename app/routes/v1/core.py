from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.clients.upstream import UpstreamClient, get_core_client
from app.config import Settings, get_settings
from app.middleware.auth import api_key_auth

router = APIRouter(dependencies=[Depends(api_key_auth)])


@router.get("/core/health", summary="Proxy core health", status_code=status.HTTP_200_OK)
async def core_health(
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    core_client: UpstreamClient = get_core_client(settings.core_api_url)
    return await core_client.request("GET", "/health")
