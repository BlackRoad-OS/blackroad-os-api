"""
Clerk Authentication Integration

Provides secure authentication and user management via Clerk.
https://clerk.com/docs
"""

import os
import httpx
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClerkUser:
    """Represents a Clerk user."""
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    email_verified: bool
    metadata: dict


@dataclass
class ClerkSession:
    """Represents a Clerk session."""
    id: str
    user_id: str
    status: str
    last_active_at: datetime
    expire_at: datetime


class ClerkClient:
    """
    Client for Clerk authentication API.

    Environment variables:
    - CLERK_SECRET_KEY: Your Clerk secret key
    - CLERK_PUBLISHABLE_KEY: Your Clerk publishable key (for frontend)
    - CLERK_WEBHOOK_SECRET: Secret for verifying webhooks
    """

    BASE_URL = "https://api.clerk.com/v1"

    def __init__(
        self,
        secret_key: Optional[str] = None,
        publishable_key: Optional[str] = None,
    ):
        self.secret_key = secret_key or os.environ.get("CLERK_SECRET_KEY")
        self.publishable_key = publishable_key or os.environ.get("CLERK_PUBLISHABLE_KEY")
        self._client: Optional[httpx.AsyncClient] = None

        if not self.secret_key:
            logger.warning("CLERK_SECRET_KEY not configured - Clerk integration disabled")

    @property
    def is_configured(self) -> bool:
        """Check if Clerk is properly configured."""
        return bool(self.secret_key)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.secret_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def verify_session(self, session_token: str) -> Optional[ClerkSession]:
        """
        Verify a session token and return session details.

        Args:
            session_token: The session token to verify

        Returns:
            ClerkSession if valid, None otherwise
        """
        if not self.is_configured:
            logger.warning("Clerk not configured, skipping session verification")
            return None

        try:
            client = await self._get_client()
            response = await client.post(
                "/sessions/verify",
                json={"token": session_token},
            )

            if response.status_code == 200:
                data = response.json()
                return ClerkSession(
                    id=data["id"],
                    user_id=data["user_id"],
                    status=data["status"],
                    last_active_at=datetime.fromisoformat(data["last_active_at"].replace("Z", "+00:00")),
                    expire_at=datetime.fromisoformat(data["expire_at"].replace("Z", "+00:00")),
                )
            else:
                logger.warning(f"Session verification failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error verifying session: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[ClerkUser]:
        """
        Get user details by ID.

        Args:
            user_id: The Clerk user ID

        Returns:
            ClerkUser if found, None otherwise
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get(f"/users/{user_id}")

            if response.status_code == 200:
                data = response.json()
                return ClerkUser(
                    id=data["id"],
                    email=data.get("email_addresses", [{}])[0].get("email_address", ""),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                    email_verified=data.get("email_addresses", [{}])[0].get("verified", False),
                    metadata=data.get("public_metadata", {}),
                )
            return None

        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def list_users(
        self,
        limit: int = 10,
        offset: int = 0,
        email_address: Optional[str] = None,
    ) -> list[ClerkUser]:
        """
        List users with optional filtering.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            email_address: Filter by email address

        Returns:
            List of ClerkUser objects
        """
        if not self.is_configured:
            return []

        try:
            client = await self._get_client()
            params = {"limit": limit, "offset": offset}
            if email_address:
                params["email_address"] = email_address

            response = await client.get("/users", params=params)

            if response.status_code == 200:
                users = []
                for data in response.json():
                    users.append(
                        ClerkUser(
                            id=data["id"],
                            email=data.get("email_addresses", [{}])[0].get("email_address", ""),
                            first_name=data.get("first_name"),
                            last_name=data.get("last_name"),
                            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                            email_verified=data.get("email_addresses", [{}])[0].get("verified", False),
                            metadata=data.get("public_metadata", {}),
                        )
                    )
                return users
            return []

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: Optional[str] = None,
    ) -> bool:
        """
        Verify a Clerk webhook signature.

        Args:
            payload: The raw request body
            signature: The Svix-Signature header
            webhook_secret: The webhook secret (or use CLERK_WEBHOOK_SECRET env var)

        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib

        secret = webhook_secret or os.environ.get("CLERK_WEBHOOK_SECRET")
        if not secret:
            logger.error("Webhook secret not configured")
            return False

        try:
            # Parse the signature header (Svix format)
            signatures = {}
            for part in signature.split(","):
                key, value = part.split("=", 1)
                signatures[key] = value

            timestamp = signatures.get("t")
            v1_signature = signatures.get("v1")

            if not timestamp or not v1_signature:
                return False

            # Compute expected signature
            signed_payload = f"{timestamp}.{payload.decode()}"
            expected = hmac.new(
                secret.encode(),
                signed_payload.encode(),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected, v1_signature)

        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return False
