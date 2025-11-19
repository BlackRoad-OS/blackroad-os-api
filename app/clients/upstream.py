from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.errors import UpstreamError

DEFAULT_TIMEOUT = 10.0


class UpstreamClient:
    """
    A client for making HTTP requests to an upstream service.

    Attributes:
        name (str): The name of the upstream service.
        base_url (Optional[str]): The base URL of the upstream service.
    """
    def __init__(self, name: str, base_url: Optional[str], default_timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize an UpstreamClient.

        Args:
            name (str): The name of the upstream service.
            base_url (Optional[str]): The base URL of the upstream service.
        """
        self.name = name
        self.base_url = base_url.rstrip("/") if base_url else None
        self.default_timeout = default_timeout

    async def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the upstream service.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            path (str): The path to append to the base URL.
            **kwargs: Additional arguments to pass to httpx.AsyncClient.request.
                Common options include 'params', 'json', 'headers', etc.
                'timeout' (float, optional): Request timeout in seconds (default: 10.0).

        Returns:
            Dict[str, Any]: The response data. If the response is JSON, returns the parsed JSON.
                Otherwise, returns a dict with 'status_code' and 'content'.

        Raises:
            UpstreamError: If the upstream is not configured, times out, returns an error status,
                or if the request fails for any reason.
        """
        if not self.base_url:
            raise UpstreamError(source=self.name, message=f"{self.name} upstream not configured", status_code=502)

        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = kwargs.pop("timeout", self.default_timeout)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            return {
                "status_code": response.status_code,
                "content": response.text,
                "content_type": response.headers.get("content-type", ""),
            }
        except httpx.TimeoutException as exc:
            raise UpstreamError(self.name, message=f"{self.name} upstream timeout", details={"path": path}) from exc
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(
                self.name,
                status_code=exc.response.status_code,
                message=f"{self.name} upstream returned {exc.response.status_code}",
                details={"path": path},
            )
        except httpx.HTTPError as exc:
            raise UpstreamError(self.name, message=f"{self.name} upstream request failed", details={"path": path}) from exc
