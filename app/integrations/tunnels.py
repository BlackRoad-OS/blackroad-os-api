"""
Tunnel Configuration Integration

Provides secure tunnel configurations for:
- Cloudflare Tunnel (cloudflared)
- ngrok
- localtunnel
- Custom tunnel solutions
"""

import os
import subprocess
import asyncio
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import logging
import json
import httpx

logger = logging.getLogger(__name__)


class TunnelProvider(Enum):
    """Supported tunnel providers."""
    CLOUDFLARE = "cloudflare"
    NGROK = "ngrok"
    LOCALTUNNEL = "localtunnel"
    CUSTOM = "custom"


@dataclass
class TunnelConfig:
    """Configuration for a tunnel."""
    provider: TunnelProvider
    name: str
    local_port: int
    subdomain: Optional[str] = None
    hostname: Optional[str] = None
    auth_token: Optional[str] = None
    extra_args: list[str] = None

    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = []


@dataclass
class TunnelStatus:
    """Status of a tunnel."""
    name: str
    provider: TunnelProvider
    is_running: bool
    public_url: Optional[str]
    local_port: int
    pid: Optional[int]
    error: Optional[str]


class TunnelManager:
    """
    Manages secure tunnels for exposing local services.

    Environment variables:
    - CLOUDFLARE_TUNNEL_TOKEN: Cloudflare tunnel token
    - NGROK_AUTH_TOKEN: ngrok authentication token
    - TUNNEL_DEFAULT_PROVIDER: Default tunnel provider
    """

    def __init__(self):
        self._tunnels: dict[str, subprocess.Popen] = {}
        self._tunnel_urls: dict[str, str] = {}

        # Load tokens from environment
        self.cloudflare_token = os.environ.get("CLOUDFLARE_TUNNEL_TOKEN")
        self.ngrok_token = os.environ.get("NGROK_AUTH_TOKEN")
        self.default_provider = TunnelProvider(
            os.environ.get("TUNNEL_DEFAULT_PROVIDER", "cloudflare")
        )

    async def start_tunnel(self, config: TunnelConfig) -> TunnelStatus:
        """
        Start a tunnel with the given configuration.

        Args:
            config: Tunnel configuration

        Returns:
            TunnelStatus with connection details
        """
        if config.name in self._tunnels:
            logger.warning(f"Tunnel {config.name} already running")
            return await self.get_status(config.name)

        try:
            if config.provider == TunnelProvider.CLOUDFLARE:
                return await self._start_cloudflare(config)
            elif config.provider == TunnelProvider.NGROK:
                return await self._start_ngrok(config)
            elif config.provider == TunnelProvider.LOCALTUNNEL:
                return await self._start_localtunnel(config)
            else:
                return TunnelStatus(
                    name=config.name,
                    provider=config.provider,
                    is_running=False,
                    public_url=None,
                    local_port=config.local_port,
                    pid=None,
                    error=f"Unsupported provider: {config.provider}",
                )
        except Exception as e:
            logger.error(f"Failed to start tunnel: {e}")
            return TunnelStatus(
                name=config.name,
                provider=config.provider,
                is_running=False,
                public_url=None,
                local_port=config.local_port,
                pid=None,
                error=str(e),
            )

    async def _start_cloudflare(self, config: TunnelConfig) -> TunnelStatus:
        """Start a Cloudflare tunnel."""
        token = config.auth_token or self.cloudflare_token

        if not token:
            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.CLOUDFLARE,
                is_running=False,
                public_url=None,
                local_port=config.local_port,
                pid=None,
                error="CLOUDFLARE_TUNNEL_TOKEN not configured",
            )

        cmd = [
            "cloudflared",
            "tunnel",
            "--url", f"http://localhost:{config.local_port}",
        ]

        if config.hostname:
            cmd.extend(["--hostname", config.hostname])

        cmd.extend(config.extra_args)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "TUNNEL_TOKEN": token},
            )

            self._tunnels[config.name] = process

            # Wait a moment for the tunnel to establish
            await asyncio.sleep(3)

            # Try to get the URL from cloudflared output
            public_url = await self._get_cloudflare_url(process)

            if public_url:
                self._tunnel_urls[config.name] = public_url

            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.CLOUDFLARE,
                is_running=process.poll() is None,
                public_url=public_url,
                local_port=config.local_port,
                pid=process.pid,
                error=None,
            )

        except FileNotFoundError:
            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.CLOUDFLARE,
                is_running=False,
                public_url=None,
                local_port=config.local_port,
                pid=None,
                error="cloudflared not installed",
            )

    async def _get_cloudflare_url(self, process: subprocess.Popen) -> Optional[str]:
        """Extract the public URL from cloudflared output."""
        try:
            # Read from stderr where cloudflared logs
            for _ in range(10):
                if process.poll() is not None:
                    break

                line = process.stderr.readline()
                if line:
                    decoded = line.decode().strip()
                    if "trycloudflare.com" in decoded or "cfargotunnel.com" in decoded:
                        # Extract URL
                        parts = decoded.split()
                        for part in parts:
                            if "http" in part:
                                return part.strip()

                await asyncio.sleep(0.5)

        except Exception as e:
            logger.warning(f"Could not get Cloudflare URL: {e}")

        return None

    async def _start_ngrok(self, config: TunnelConfig) -> TunnelStatus:
        """Start an ngrok tunnel."""
        token = config.auth_token or self.ngrok_token

        cmd = ["ngrok", "http", str(config.local_port)]

        if token:
            cmd.extend(["--authtoken", token])

        if config.subdomain:
            cmd.extend(["--subdomain", config.subdomain])

        cmd.extend(config.extra_args)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self._tunnels[config.name] = process

            # Wait for ngrok to start
            await asyncio.sleep(3)

            # Get URL from ngrok API
            public_url = await self._get_ngrok_url()

            if public_url:
                self._tunnel_urls[config.name] = public_url

            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.NGROK,
                is_running=process.poll() is None,
                public_url=public_url,
                local_port=config.local_port,
                pid=process.pid,
                error=None,
            )

        except FileNotFoundError:
            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.NGROK,
                is_running=False,
                public_url=None,
                local_port=config.local_port,
                pid=None,
                error="ngrok not installed",
            )

    async def _get_ngrok_url(self) -> Optional[str]:
        """Get the public URL from ngrok's local API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:4040/api/tunnels")
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    for tunnel in tunnels:
                        if tunnel.get("proto") == "https":
                            return tunnel.get("public_url")
                        elif tunnel.get("public_url"):
                            return tunnel.get("public_url")
        except Exception as e:
            logger.warning(f"Could not get ngrok URL: {e}")

        return None

    async def _start_localtunnel(self, config: TunnelConfig) -> TunnelStatus:
        """Start a localtunnel."""
        cmd = ["lt", "--port", str(config.local_port)]

        if config.subdomain:
            cmd.extend(["--subdomain", config.subdomain])

        cmd.extend(config.extra_args)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self._tunnels[config.name] = process

            # Wait for tunnel to start
            await asyncio.sleep(3)

            # Try to get URL from output
            public_url = None
            try:
                line = process.stdout.readline().decode().strip()
                if "https://" in line:
                    public_url = line.split()[-1]
            except Exception:
                pass

            if public_url:
                self._tunnel_urls[config.name] = public_url

            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.LOCALTUNNEL,
                is_running=process.poll() is None,
                public_url=public_url,
                local_port=config.local_port,
                pid=process.pid,
                error=None,
            )

        except FileNotFoundError:
            return TunnelStatus(
                name=config.name,
                provider=TunnelProvider.LOCALTUNNEL,
                is_running=False,
                public_url=None,
                local_port=config.local_port,
                pid=None,
                error="localtunnel (lt) not installed",
            )

    async def stop_tunnel(self, name: str) -> bool:
        """
        Stop a running tunnel.

        Args:
            name: Tunnel name

        Returns:
            True if stopped successfully
        """
        if name not in self._tunnels:
            logger.warning(f"Tunnel {name} not found")
            return False

        try:
            process = self._tunnels[name]
            process.terminate()
            process.wait(timeout=5)
            del self._tunnels[name]

            if name in self._tunnel_urls:
                del self._tunnel_urls[name]

            return True

        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")
            return False

    async def stop_all(self):
        """Stop all running tunnels."""
        for name in list(self._tunnels.keys()):
            await self.stop_tunnel(name)

    async def get_status(self, name: str) -> Optional[TunnelStatus]:
        """
        Get status of a tunnel.

        Args:
            name: Tunnel name

        Returns:
            TunnelStatus if found
        """
        if name not in self._tunnels:
            return None

        process = self._tunnels[name]
        is_running = process.poll() is None

        return TunnelStatus(
            name=name,
            provider=TunnelProvider.CLOUDFLARE,  # Would need to track this
            is_running=is_running,
            public_url=self._tunnel_urls.get(name),
            local_port=0,  # Would need to track this
            pid=process.pid if is_running else None,
            error=None if is_running else "Process terminated",
        )

    def list_tunnels(self) -> list[str]:
        """List all active tunnel names."""
        return list(self._tunnels.keys())

    def get_quick_tunnel_config(
        self,
        local_port: int,
        name: str = "default",
        provider: Optional[TunnelProvider] = None,
    ) -> TunnelConfig:
        """
        Get a quick tunnel configuration.

        Args:
            local_port: Local port to expose
            name: Tunnel name
            provider: Tunnel provider (uses default if not specified)

        Returns:
            TunnelConfig ready to use
        """
        return TunnelConfig(
            provider=provider or self.default_provider,
            name=name,
            local_port=local_port,
        )


# Cloudflare Tunnel configuration generator
def generate_cloudflare_config(
    tunnel_name: str,
    tunnel_id: str,
    ingress_rules: list[dict],
    credentials_file: str = "/etc/cloudflared/credentials.json",
) -> dict:
    """
    Generate a Cloudflare Tunnel configuration.

    Args:
        tunnel_name: Name of the tunnel
        tunnel_id: Cloudflare tunnel ID
        ingress_rules: List of ingress rules
        credentials_file: Path to credentials file

    Returns:
        Configuration dict (can be written to YAML)
    """
    return {
        "tunnel": tunnel_id,
        "credentials-file": credentials_file,
        "ingress": [
            *ingress_rules,
            {"service": "http_status:404"},  # Catch-all rule
        ],
    }
