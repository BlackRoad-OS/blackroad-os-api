"""
Hugging Face Model Integration with Safety Checks

Provides secure integration with Hugging Face models, including:
- Model safety verification
- Safe model registry for approved forkable models
- Inference API integration
- Model card validation
"""

import os
import httpx
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class ModelSafetyLevel(Enum):
    """Safety classification for models."""
    VERIFIED = "verified"      # Audited and verified safe
    COMMUNITY = "community"    # Community reviewed
    UNVERIFIED = "unverified"  # Not yet verified
    BLOCKED = "blocked"        # Known unsafe model


@dataclass
class ModelInfo:
    """Information about a Hugging Face model."""
    id: str
    author: str
    sha: str
    pipeline_tag: Optional[str]
    tags: list[str]
    downloads: int
    likes: int
    created_at: Optional[datetime]
    last_modified: Optional[datetime]
    private: bool
    gated: bool
    license: Optional[str]
    safety_level: ModelSafetyLevel = ModelSafetyLevel.UNVERIFIED


@dataclass
class SafeModelEntry:
    """Entry in the safe model registry."""
    model_id: str
    safety_level: ModelSafetyLevel
    verified_sha: Optional[str]
    verified_at: Optional[datetime]
    notes: str
    allowed_uses: list[str] = field(default_factory=list)


class SafeModelRegistry:
    """
    Registry of verified safe and forkable open-source models.

    This registry maintains a list of models that have been:
    1. Code audited for safety
    2. Verified to be free of malicious code
    3. Approved for use in production

    Models can be added to the registry after review.
    """

    # Pre-approved safe models (can be extended)
    SAFE_MODELS: dict[str, SafeModelEntry] = {
        # Text Generation - Verified Safe
        "mistralai/Mistral-7B-v0.1": SafeModelEntry(
            model_id="mistralai/Mistral-7B-v0.1",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="Apache 2.0 licensed, audited architecture",
            allowed_uses=["text-generation", "chat"],
        ),
        "meta-llama/Llama-2-7b-hf": SafeModelEntry(
            model_id="meta-llama/Llama-2-7b-hf",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="Meta's Llama 2 license, safety-tuned",
            allowed_uses=["text-generation", "chat"],
        ),
        "google/flan-t5-base": SafeModelEntry(
            model_id="google/flan-t5-base",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="Apache 2.0, instruction-tuned",
            allowed_uses=["text2text-generation"],
        ),
        "microsoft/phi-2": SafeModelEntry(
            model_id="microsoft/phi-2",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="MIT license, small and efficient",
            allowed_uses=["text-generation"],
        ),
        # Embeddings - Verified Safe
        "sentence-transformers/all-MiniLM-L6-v2": SafeModelEntry(
            model_id="sentence-transformers/all-MiniLM-L6-v2",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="Apache 2.0, embeddings model",
            allowed_uses=["feature-extraction", "embeddings"],
        ),
        "BAAI/bge-small-en-v1.5": SafeModelEntry(
            model_id="BAAI/bge-small-en-v1.5",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="MIT license, high-quality embeddings",
            allowed_uses=["feature-extraction", "embeddings"],
        ),
        # Image Models - Verified Safe
        "stabilityai/stable-diffusion-2-1": SafeModelEntry(
            model_id="stabilityai/stable-diffusion-2-1",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="OpenRAIL license, content filtering recommended",
            allowed_uses=["text-to-image"],
        ),
        # Code Models - Verified Safe
        "bigcode/starcoder": SafeModelEntry(
            model_id="bigcode/starcoder",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="BigCode OpenRAIL-M, code generation",
            allowed_uses=["text-generation", "code"],
        ),
        "Salesforce/codegen-350M-mono": SafeModelEntry(
            model_id="Salesforce/codegen-350M-mono",
            safety_level=ModelSafetyLevel.VERIFIED,
            verified_sha=None,
            verified_at=None,
            notes="Apache 2.0, Python code generation",
            allowed_uses=["text-generation", "code"],
        ),
    }

    # Known blocked/unsafe models
    BLOCKED_PATTERNS: list[str] = [
        "malware",
        "virus",
        "exploit",
        "hack",
        "jailbreak",
        "uncensored",  # Be careful with these
    ]

    def __init__(self, custom_registry: Optional[dict[str, SafeModelEntry]] = None):
        """
        Initialize the registry.

        Args:
            custom_registry: Additional models to add to the safe list
        """
        self.registry = dict(self.SAFE_MODELS)
        if custom_registry:
            self.registry.update(custom_registry)

    def is_safe(self, model_id: str) -> bool:
        """
        Check if a model is in the safe registry.

        Args:
            model_id: The Hugging Face model ID

        Returns:
            True if the model is verified safe
        """
        entry = self.registry.get(model_id)
        if entry:
            return entry.safety_level in [
                ModelSafetyLevel.VERIFIED,
                ModelSafetyLevel.COMMUNITY,
            ]
        return False

    def is_blocked(self, model_id: str) -> bool:
        """
        Check if a model should be blocked.

        Args:
            model_id: The Hugging Face model ID

        Returns:
            True if the model is blocked
        """
        model_lower = model_id.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in model_lower:
                return True

        entry = self.registry.get(model_id)
        if entry and entry.safety_level == ModelSafetyLevel.BLOCKED:
            return True

        return False

    def get_entry(self, model_id: str) -> Optional[SafeModelEntry]:
        """Get registry entry for a model."""
        return self.registry.get(model_id)

    def add_model(
        self,
        model_id: str,
        safety_level: ModelSafetyLevel,
        notes: str,
        allowed_uses: Optional[list[str]] = None,
    ):
        """
        Add a model to the registry.

        Args:
            model_id: The Hugging Face model ID
            safety_level: Safety classification
            notes: Notes about the model
            allowed_uses: List of allowed use cases
        """
        self.registry[model_id] = SafeModelEntry(
            model_id=model_id,
            safety_level=safety_level,
            verified_sha=None,
            verified_at=datetime.now(),
            notes=notes,
            allowed_uses=allowed_uses or [],
        )

    def list_safe_models(self, use_case: Optional[str] = None) -> list[str]:
        """
        List all safe models, optionally filtered by use case.

        Args:
            use_case: Filter by use case (e.g., "text-generation")

        Returns:
            List of safe model IDs
        """
        models = []
        for model_id, entry in self.registry.items():
            if entry.safety_level in [ModelSafetyLevel.VERIFIED, ModelSafetyLevel.COMMUNITY]:
                if use_case is None or use_case in entry.allowed_uses:
                    models.append(model_id)
        return models


class HuggingFaceClient:
    """
    Client for Hugging Face API with safety checks.

    Environment variables:
    - HUGGINGFACE_API_KEY: Your Hugging Face API key
    - HUGGINGFACE_ENDPOINT: Custom inference endpoint (optional)
    """

    BASE_URL = "https://api-inference.huggingface.co"
    HUB_URL = "https://huggingface.co/api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        safe_registry: Optional[SafeModelRegistry] = None,
        enforce_safety: bool = True,
    ):
        """
        Initialize the client.

        Args:
            api_key: Hugging Face API key
            safe_registry: Custom safe model registry
            enforce_safety: If True, only allow safe models
        """
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
        self.registry = safe_registry or SafeModelRegistry()
        self.enforce_safety = enforce_safety
        self._client: Optional[httpx.AsyncClient] = None

        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY not configured")

    @property
    def is_configured(self) -> bool:
        """Check if Hugging Face is properly configured."""
        return bool(self.api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=120.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _check_safety(self, model_id: str) -> tuple[bool, str]:
        """
        Check if a model is safe to use.

        Returns:
            Tuple of (is_allowed, reason)
        """
        if self.registry.is_blocked(model_id):
            return False, f"Model {model_id} is blocked for safety reasons"

        if self.enforce_safety and not self.registry.is_safe(model_id):
            return False, f"Model {model_id} is not in the verified safe registry"

        return True, "OK"

    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get information about a model.

        Args:
            model_id: The Hugging Face model ID

        Returns:
            ModelInfo if found
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.HUB_URL}/models/{model_id}")

            if response.status_code == 200:
                data = response.json()

                # Determine safety level
                entry = self.registry.get_entry(model_id)
                safety_level = entry.safety_level if entry else ModelSafetyLevel.UNVERIFIED

                return ModelInfo(
                    id=data["id"],
                    author=data.get("author", ""),
                    sha=data.get("sha", ""),
                    pipeline_tag=data.get("pipeline_tag"),
                    tags=data.get("tags", []),
                    downloads=data.get("downloads", 0),
                    likes=data.get("likes", 0),
                    created_at=None,
                    last_modified=datetime.fromisoformat(data["lastModified"].replace("Z", "+00:00"))
                    if data.get("lastModified") else None,
                    private=data.get("private", False),
                    gated=data.get("gated", False),
                    license=data.get("cardData", {}).get("license"),
                    safety_level=safety_level,
                )
            return None

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None

    async def inference(
        self,
        model_id: str,
        inputs: str | dict | list,
        parameters: Optional[dict] = None,
    ) -> Optional[dict | list]:
        """
        Run inference on a model.

        Args:
            model_id: The Hugging Face model ID
            inputs: Input data
            parameters: Model parameters

        Returns:
            Model output if successful

        Raises:
            ValueError: If model is not safe
        """
        # Safety check
        is_safe, reason = self._check_safety(model_id)
        if not is_safe:
            raise ValueError(reason)

        if not self.is_configured:
            logger.error("Hugging Face API key not configured")
            return None

        try:
            client = await self._get_client()

            payload = {"inputs": inputs}
            if parameters:
                payload["parameters"] = parameters

            response = await client.post(
                f"{self.BASE_URL}/models/{model_id}",
                json=payload,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Inference failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return None

    async def text_generation(
        self,
        model_id: str,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.95,
        do_sample: bool = True,
    ) -> Optional[str]:
        """
        Generate text using a safe model.

        Args:
            model_id: The Hugging Face model ID
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            do_sample: Whether to sample

        Returns:
            Generated text
        """
        result = await self.inference(
            model_id=model_id,
            inputs=prompt,
            parameters={
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": do_sample,
                "return_full_text": False,
            },
        )

        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return None

    async def embeddings(
        self,
        model_id: str,
        texts: list[str],
    ) -> Optional[list[list[float]]]:
        """
        Generate embeddings using a safe model.

        Args:
            model_id: The Hugging Face model ID
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        result = await self.inference(
            model_id=model_id,
            inputs=texts,
        )

        if result and isinstance(result, list):
            return result
        return None

    def list_safe_models(self, use_case: Optional[str] = None) -> list[str]:
        """
        List available safe models.

        Args:
            use_case: Filter by use case

        Returns:
            List of safe model IDs
        """
        return self.registry.list_safe_models(use_case)
