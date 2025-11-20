from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import httpx
from fastapi import Request, Response

HOP_BY_HOP_HEADERS = {
    "host",
    "content-length",
    "accept-encoding",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


@dataclass
class ProxyPayload:
    params: Sequence[Tuple[str, str]]
    headers: Mapping[str, str]
    body: Optional[bytes]
    json: Optional[Any]


async def extract_proxy_payload(request: Request) -> ProxyPayload:
    raw_body = await request.body()
    content_type = request.headers.get("content-type", "")
    json_body: Optional[Any] = None

    if raw_body and "application/json" in content_type.lower():
        try:
            json_body = json.loads(raw_body.decode())
            raw_body = None
        except (ValueError, UnicodeDecodeError):
            json_body = None

    filtered_headers: Dict[str, str] = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    return ProxyPayload(
        params=list(request.query_params.multi_items()),
        headers=filtered_headers,
        body=raw_body if raw_body else None,
        json=json_body,
    )


def build_proxy_response(upstream_response: httpx.Response) -> Response:
    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() in {"content-type"}
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
