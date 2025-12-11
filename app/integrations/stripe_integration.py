"""
Stripe Payment Integration

Provides secure payment processing via Stripe.
https://stripe.com/docs/api
"""

import os
import httpx
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class StripeCustomer:
    """Represents a Stripe customer."""
    id: str
    email: str
    name: Optional[str]
    created: datetime
    metadata: dict


@dataclass
class StripePaymentIntent:
    """Represents a Stripe payment intent."""
    id: str
    amount: int
    currency: str
    status: str
    customer_id: Optional[str]
    created: datetime
    client_secret: str


@dataclass
class StripeSubscription:
    """Represents a Stripe subscription."""
    id: str
    customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    items: list[dict]


class StripeClient:
    """
    Client for Stripe payment API.

    Environment variables:
    - STRIPE_SECRET_KEY: Your Stripe secret key
    - STRIPE_PUBLISHABLE_KEY: Your Stripe publishable key (for frontend)
    - STRIPE_WEBHOOK_SECRET: Secret for verifying webhooks
    """

    BASE_URL = "https://api.stripe.com/v1"

    def __init__(
        self,
        secret_key: Optional[str] = None,
        publishable_key: Optional[str] = None,
    ):
        self.secret_key = secret_key or os.environ.get("STRIPE_SECRET_KEY")
        self.publishable_key = publishable_key or os.environ.get("STRIPE_PUBLISHABLE_KEY")
        self._client: Optional[httpx.AsyncClient] = None

        if not self.secret_key:
            logger.warning("STRIPE_SECRET_KEY not configured - Stripe integration disabled")

    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.secret_key)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                auth=(self.secret_key, ""),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[StripeCustomer]:
        """
        Create a new Stripe customer.

        Args:
            email: Customer email address
            name: Customer name
            metadata: Additional metadata

        Returns:
            StripeCustomer if successful
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            data = {"email": email}
            if name:
                data["name"] = name
            if metadata:
                for key, value in metadata.items():
                    data[f"metadata[{key}]"] = value

            response = await client.post("/customers", data=data)

            if response.status_code == 200:
                result = response.json()
                return StripeCustomer(
                    id=result["id"],
                    email=result["email"],
                    name=result.get("name"),
                    created=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {}),
                )
            else:
                logger.error(f"Failed to create customer: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[StripePaymentIntent]:
        """
        Create a payment intent.

        Args:
            amount: Amount in cents
            currency: Three-letter currency code
            customer_id: Optional customer ID
            metadata: Additional metadata

        Returns:
            StripePaymentIntent if successful
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            data = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods[enabled]": "true",
            }
            if customer_id:
                data["customer"] = customer_id
            if metadata:
                for key, value in metadata.items():
                    data[f"metadata[{key}]"] = value

            response = await client.post("/payment_intents", data=data)

            if response.status_code == 200:
                result = response.json()
                return StripePaymentIntent(
                    id=result["id"],
                    amount=result["amount"],
                    currency=result["currency"],
                    status=result["status"],
                    customer_id=result.get("customer"),
                    created=datetime.fromtimestamp(result["created"]),
                    client_secret=result["client_secret"],
                )
            else:
                logger.error(f"Failed to create payment intent: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return None

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
    ) -> Optional[StripeSubscription]:
        """
        Create a subscription.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Optional trial period in days

        Returns:
            StripeSubscription if successful
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            data = {
                "customer": customer_id,
                "items[0][price]": price_id,
            }
            if trial_days:
                data["trial_period_days"] = trial_days

            response = await client.post("/subscriptions", data=data)

            if response.status_code == 200:
                result = response.json()
                return StripeSubscription(
                    id=result["id"],
                    customer_id=result["customer"],
                    status=result["status"],
                    current_period_start=datetime.fromtimestamp(result["current_period_start"]),
                    current_period_end=datetime.fromtimestamp(result["current_period_end"]),
                    cancel_at_period_end=result["cancel_at_period_end"],
                    items=[item["price"] for item in result["items"]["data"]],
                )
            else:
                logger.error(f"Failed to create subscription: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None

    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
    ) -> bool:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of billing period

        Returns:
            True if successful
        """
        if not self.is_configured:
            return False

        try:
            client = await self._get_client()

            if at_period_end:
                response = await client.post(
                    f"/subscriptions/{subscription_id}",
                    data={"cancel_at_period_end": "true"},
                )
            else:
                response = await client.delete(f"/subscriptions/{subscription_id}")

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: Optional[str] = None,
    ) -> bool:
        """
        Verify a Stripe webhook signature.

        Args:
            payload: The raw request body
            signature: The Stripe-Signature header
            webhook_secret: The webhook secret (or use STRIPE_WEBHOOK_SECRET env var)

        Returns:
            True if signature is valid
        """
        secret = webhook_secret or os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not secret:
            logger.error("Webhook secret not configured")
            return False

        try:
            # Parse the signature header
            signatures = {}
            for part in signature.split(","):
                key, value = part.split("=", 1)
                signatures[key.strip()] = value.strip()

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

    async def get_balance(self) -> Optional[dict]:
        """
        Get Stripe account balance.

        Returns:
            Balance information if successful
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get("/balance")

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None
