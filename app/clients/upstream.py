from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.errors import UpstreamError

DEFAULT_TIMEOUT = 10.0


class UpstreamClient:
    def __init__(self, name: str, base_url: Optional[str]):
        self.name = name
        self.base_url = base_url.rstrip("/") if base_url else None

    async def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        if not self.base_url:
            raise UpstreamError(source=self.name, message=f"{self.name} upstream not configured", status_code=502)

        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            return {"status_code": response.status_code, "content": response.text}
        except httpx.TimeoutException as exc:
            raise UpstreamError(self.name, message=f"{self.name} upstream timeout", details={"path": path}) from exc
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(
                self.name,
                status_code=exc.response.status_code,
                message=f"{self.name} upstream returned {exc.response.status_code}",
                details={"path": path},
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamError(self.name, message=f"{self.name} upstream request failed", details={"path": path}) from exc


def get_core_client(core_api_url: Optional[str]) -> UpstreamClient:
    return UpstreamClient("core", core_api_url)


def get_agents_client(agents_api_url: Optional[str]) -> UpstreamClient:
    return UpstreamClient("agents", agents_api_url)
