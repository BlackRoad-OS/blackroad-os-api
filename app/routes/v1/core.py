from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response, status

from app.clients.core_client import build_core_client
from app.config import Settings, get_settings
from app.routes.v1.shared import build_proxy_response, extract_proxy_payload

router = APIRouter(prefix="/core")


@router.get("/ping", summary="Proxy core ping", status_code=status.HTTP_200_OK)
async def core_ping(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    core_client = build_core_client(settings)
    return await core_client.request("GET", "/ping")


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"], summary="Proxy Core API")
async def proxy_core(
    full_path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Response:
    core_client = build_core_client(settings)
    proxy_payload = await extract_proxy_payload(request)
    upstream_response = await core_client.proxy_request(
        request.method,
        full_path,
        params=proxy_payload.params,
        headers=proxy_payload.headers,
        content=proxy_payload.body,
        json=proxy_payload.json,
    )
    return build_proxy_response(upstream_response)
