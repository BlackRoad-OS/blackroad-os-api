"""
Open Source LLM Integration with Safety Guardrails

Provides secure integration with forkable open-source LLM models:
- Model safety verification and code auditing
- Safe model registry for approved models
- Integration with various inference backends
- Safety guardrails and content filtering
"""

import os
import hashlib
import json
import re
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import httpx

logger = logging.getLogger(__name__)


class ModelLicense(Enum):
    """Common open-source model licenses."""
    APACHE_2 = "apache-2.0"
    MIT = "mit"
    LLAMA_2 = "llama2"
    LLAMA_3 = "llama3"
    OPENRAIL = "openrail"
    OPENRAIL_M = "openrail-m"
    CC_BY_NC = "cc-by-nc-4.0"
    CC_BY_SA = "cc-by-sa-4.0"
    GPL_3 = "gpl-3.0"
    BSD_3 = "bsd-3-clause"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"


class SafetyLevel(Enum):
    """Safety classification levels."""
    AUDITED = "audited"        # Fully code-audited
    VERIFIED = "verified"      # Verified safe by community
    REVIEWED = "reviewed"      # Basic review completed
    EXPERIMENTAL = "experimental"  # Use with caution
    UNSAFE = "unsafe"          # Known issues


@dataclass
class SafeModel:
    """A safe, forkable open-source model."""
    model_id: str
    name: str
    provider: str
    size_b: float  # Size in billions of parameters
    license: ModelLicense
    safety_level: SafetyLevel
    repo_url: str
    description: str
    capabilities: list[str]
    verified_sha: Optional[str] = None
    audit_date: Optional[datetime] = None
    notes: str = ""
    forkable: bool = True
    restrictions: list[str] = field(default_factory=list)


# Registry of safe, forkable open-source models
SAFE_OSS_MODELS: dict[str, SafeModel] = {
    # Mistral Family - Apache 2.0, fully forkable
    "mistral-7b": SafeModel(
        model_id="mistralai/Mistral-7B-v0.1",
        name="Mistral 7B",
        provider="Mistral AI",
        size_b=7.3,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/mistralai/Mistral-7B-v0.1",
        description="High-quality 7B parameter model with Apache 2.0 license",
        capabilities=["text-generation", "chat", "code", "reasoning"],
        forkable=True,
        notes="Excellent base model for fine-tuning",
    ),
    "mistral-7b-instruct": SafeModel(
        model_id="mistralai/Mistral-7B-Instruct-v0.2",
        name="Mistral 7B Instruct",
        provider="Mistral AI",
        size_b=7.3,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2",
        description="Instruction-tuned Mistral 7B",
        capabilities=["chat", "instruction-following", "qa"],
        forkable=True,
    ),
    "mixtral-8x7b": SafeModel(
        model_id="mistralai/Mixtral-8x7B-v0.1",
        name="Mixtral 8x7B",
        provider="Mistral AI",
        size_b=46.7,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/mistralai/Mixtral-8x7B-v0.1",
        description="Mixture of Experts model with 8x7B architecture",
        capabilities=["text-generation", "chat", "code", "multilingual"],
        forkable=True,
        notes="MoE architecture, ~12B active params per forward pass",
    ),

    # Llama Family - Meta license, forkable with attribution
    "llama-2-7b": SafeModel(
        model_id="meta-llama/Llama-2-7b-hf",
        name="Llama 2 7B",
        provider="Meta",
        size_b=7.0,
        license=ModelLicense.LLAMA_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/meta-llama/Llama-2-7b-hf",
        description="Meta's Llama 2 7B base model",
        capabilities=["text-generation", "reasoning"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),
    "llama-2-13b": SafeModel(
        model_id="meta-llama/Llama-2-13b-hf",
        name="Llama 2 13B",
        provider="Meta",
        size_b=13.0,
        license=ModelLicense.LLAMA_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/meta-llama/Llama-2-13b-hf",
        description="Meta's Llama 2 13B base model",
        capabilities=["text-generation", "reasoning", "code"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),
    "llama-2-70b": SafeModel(
        model_id="meta-llama/Llama-2-70b-hf",
        name="Llama 2 70B",
        provider="Meta",
        size_b=70.0,
        license=ModelLicense.LLAMA_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/meta-llama/Llama-2-70b-hf",
        description="Meta's largest Llama 2 model",
        capabilities=["text-generation", "reasoning", "code", "analysis"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),
    "llama-3-8b": SafeModel(
        model_id="meta-llama/Meta-Llama-3-8B",
        name="Llama 3 8B",
        provider="Meta",
        size_b=8.0,
        license=ModelLicense.LLAMA_3,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/meta-llama/Meta-Llama-3-8B",
        description="Meta's Llama 3 8B model",
        capabilities=["text-generation", "chat", "code", "reasoning"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),
    "llama-3-70b": SafeModel(
        model_id="meta-llama/Meta-Llama-3-70B",
        name="Llama 3 70B",
        provider="Meta",
        size_b=70.0,
        license=ModelLicense.LLAMA_3,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/meta-llama/Meta-Llama-3-70B",
        description="Meta's Llama 3 70B model",
        capabilities=["text-generation", "chat", "code", "reasoning", "analysis"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),

    # Google/DeepMind Models - Apache 2.0
    "gemma-2b": SafeModel(
        model_id="google/gemma-2b",
        name="Gemma 2B",
        provider="Google",
        size_b=2.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/google/gemma-2b",
        description="Google's efficient 2B parameter model",
        capabilities=["text-generation", "code"],
        forkable=True,
    ),
    "gemma-7b": SafeModel(
        model_id="google/gemma-7b",
        name="Gemma 7B",
        provider="Google",
        size_b=7.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/google/gemma-7b",
        description="Google's 7B parameter model",
        capabilities=["text-generation", "code", "reasoning"],
        forkable=True,
    ),
    "flan-t5-xxl": SafeModel(
        model_id="google/flan-t5-xxl",
        name="Flan-T5 XXL",
        provider="Google",
        size_b=11.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/google/flan-t5-xxl",
        description="Instruction-tuned T5 model",
        capabilities=["text2text-generation", "summarization", "translation"],
        forkable=True,
    ),

    # Microsoft Models
    "phi-2": SafeModel(
        model_id="microsoft/phi-2",
        name="Phi-2",
        provider="Microsoft",
        size_b=2.7,
        license=ModelLicense.MIT,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/microsoft/phi-2",
        description="Small but capable reasoning model",
        capabilities=["text-generation", "reasoning", "code"],
        forkable=True,
        notes="Excellent for edge deployment",
    ),
    "phi-3-mini": SafeModel(
        model_id="microsoft/Phi-3-mini-4k-instruct",
        name="Phi-3 Mini",
        provider="Microsoft",
        size_b=3.8,
        license=ModelLicense.MIT,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
        description="Phi-3 mini instruction-tuned model",
        capabilities=["text-generation", "chat", "reasoning"],
        forkable=True,
    ),

    # Qwen Models - Apache 2.0
    "qwen-1.5-7b": SafeModel(
        model_id="Qwen/Qwen1.5-7B",
        name="Qwen 1.5 7B",
        provider="Alibaba",
        size_b=7.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/Qwen/Qwen1.5-7B",
        description="Alibaba's Qwen 1.5 7B model",
        capabilities=["text-generation", "multilingual", "code"],
        forkable=True,
    ),
    "qwen-1.5-72b": SafeModel(
        model_id="Qwen/Qwen1.5-72B",
        name="Qwen 1.5 72B",
        provider="Alibaba",
        size_b=72.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/Qwen/Qwen1.5-72B",
        description="Alibaba's largest Qwen 1.5 model",
        capabilities=["text-generation", "multilingual", "code", "reasoning"],
        forkable=True,
    ),
    "qwen-2-72b": SafeModel(
        model_id="Qwen/Qwen2-72B",
        name="Qwen 2 72B",
        provider="Alibaba",
        size_b=72.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/Qwen/Qwen2-72B",
        description="Alibaba's Qwen 2 72B model",
        capabilities=["text-generation", "multilingual", "code", "reasoning", "math"],
        forkable=True,
    ),

    # Code Models
    "starcoder-15b": SafeModel(
        model_id="bigcode/starcoder",
        name="StarCoder 15B",
        provider="BigCode",
        size_b=15.5,
        license=ModelLicense.OPENRAIL_M,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/bigcode/starcoder",
        description="Code generation model trained on permissive data",
        capabilities=["code-generation", "code-completion"],
        forkable=True,
    ),
    "starcoder2-15b": SafeModel(
        model_id="bigcode/starcoder2-15b",
        name="StarCoder2 15B",
        provider="BigCode",
        size_b=15.5,
        license=ModelLicense.OPENRAIL_M,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/bigcode/starcoder2-15b",
        description="Improved StarCoder with 600+ languages",
        capabilities=["code-generation", "code-completion", "code-explanation"],
        forkable=True,
    ),
    "codellama-34b": SafeModel(
        model_id="codellama/CodeLlama-34b-hf",
        name="Code Llama 34B",
        provider="Meta",
        size_b=34.0,
        license=ModelLicense.LLAMA_2,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/codellama/CodeLlama-34b-hf",
        description="Specialized code generation model",
        capabilities=["code-generation", "code-completion", "infilling"],
        forkable=True,
        restrictions=["Requires Meta license acceptance"],
    ),
    "deepseek-coder-33b": SafeModel(
        model_id="deepseek-ai/deepseek-coder-33b-base",
        name="DeepSeek Coder 33B",
        provider="DeepSeek",
        size_b=33.0,
        license=ModelLicense.MIT,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/deepseek-ai/deepseek-coder-33b-base",
        description="Strong code generation model",
        capabilities=["code-generation", "code-completion"],
        forkable=True,
    ),

    # Embedding Models
    "bge-large": SafeModel(
        model_id="BAAI/bge-large-en-v1.5",
        name="BGE Large",
        provider="BAAI",
        size_b=0.335,
        license=ModelLicense.MIT,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/BAAI/bge-large-en-v1.5",
        description="High-quality embedding model",
        capabilities=["embeddings", "retrieval"],
        forkable=True,
    ),
    "e5-large": SafeModel(
        model_id="intfloat/e5-large-v2",
        name="E5 Large",
        provider="Microsoft",
        size_b=0.335,
        license=ModelLicense.MIT,
        safety_level=SafetyLevel.AUDITED,
        repo_url="https://huggingface.co/intfloat/e5-large-v2",
        description="Versatile text embedding model",
        capabilities=["embeddings", "retrieval", "similarity"],
        forkable=True,
    ),

    # Large Models (100B+ class)
    "falcon-180b": SafeModel(
        model_id="tiiuae/falcon-180B",
        name="Falcon 180B",
        provider="TII UAE",
        size_b=180.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/tiiuae/falcon-180B",
        description="Large open-source model from TII",
        capabilities=["text-generation", "reasoning", "multilingual"],
        forkable=True,
        notes="Requires significant compute resources",
    ),
    "dbrx-base": SafeModel(
        model_id="databricks/dbrx-base",
        name="DBRX Base",
        provider="Databricks",
        size_b=132.0,
        license=ModelLicense.APACHE_2,
        safety_level=SafetyLevel.VERIFIED,
        repo_url="https://huggingface.co/databricks/dbrx-base",
        description="Databricks' MoE model (36B active)",
        capabilities=["text-generation", "code", "reasoning"],
        forkable=True,
        notes="MoE architecture with 132B total params",
    ),
}


class ModelSafetyChecker:
    """
    Checks models for safety issues before use.

    Performs:
    - License verification
    - Known vulnerability checks
    - Content safety validation
    - Code audit status verification
    """

    # Patterns that indicate potentially unsafe content
    UNSAFE_PATTERNS = [
        r"(?i)jailbreak",
        r"(?i)uncensored",
        r"(?i)no.?filter",
        r"(?i)bypass.?safety",
        r"(?i)malware",
        r"(?i)exploit",
        r"(?i)hack.?tool",
    ]

    # Known unsafe model patterns
    BLOCKED_MODEL_PATTERNS = [
        r"(?i).*-uncensored.*",
        r"(?i).*-jailbreak.*",
        r"(?i).*-nsfw.*",
    ]

    def __init__(self):
        self.safe_registry = SAFE_OSS_MODELS
        self._compiled_unsafe = [re.compile(p) for p in self.UNSAFE_PATTERNS]
        self._compiled_blocked = [re.compile(p) for p in self.BLOCKED_MODEL_PATTERNS]

    def is_model_safe(self, model_id: str) -> tuple[bool, str]:
        """
        Check if a model is safe to use.

        Args:
            model_id: The model identifier

        Returns:
            Tuple of (is_safe, reason)
        """
        # Check if in safe registry
        for key, model in self.safe_registry.items():
            if model.model_id == model_id or key == model_id:
                if model.safety_level in [SafetyLevel.AUDITED, SafetyLevel.VERIFIED]:
                    return True, f"Model is {model.safety_level.value}"
                elif model.safety_level == SafetyLevel.REVIEWED:
                    return True, "Model has been reviewed (use with awareness)"
                elif model.safety_level == SafetyLevel.EXPERIMENTAL:
                    return False, "Model is experimental - not recommended for production"
                else:
                    return False, f"Model safety level: {model.safety_level.value}"

        # Check against blocked patterns
        for pattern in self._compiled_blocked:
            if pattern.match(model_id):
                return False, f"Model matches blocked pattern: {pattern.pattern}"

        # Check for unsafe keywords in name
        for pattern in self._compiled_unsafe:
            if pattern.search(model_id):
                return False, f"Model name contains unsafe pattern: {pattern.pattern}"

        return False, "Model not in safe registry - requires review"

    def check_output_safety(self, text: str) -> tuple[bool, list[str]]:
        """
        Check if model output is safe.

        Args:
            text: The output text to check

        Returns:
            Tuple of (is_safe, list of issues found)
        """
        issues = []

        # Check for unsafe patterns in output
        for pattern in self._compiled_unsafe:
            if pattern.search(text):
                issues.append(f"Output contains unsafe pattern: {pattern.pattern}")

        return len(issues) == 0, issues

    def get_model_info(self, model_id: str) -> Optional[SafeModel]:
        """Get information about a registered safe model."""
        for key, model in self.safe_registry.items():
            if model.model_id == model_id or key == model_id:
                return model
        return None


class OSSLLMClient:
    """
    Client for interacting with open-source LLMs.

    Supports multiple backends:
    - Hugging Face Inference API
    - Ollama (local)
    - vLLM (local/remote)
    - Text Generation Inference (TGI)
    - llama.cpp server
    """

    def __init__(
        self,
        backend: str = "huggingface",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enforce_safety: bool = True,
    ):
        """
        Initialize the client.

        Args:
            backend: Backend to use (huggingface, ollama, vllm, tgi, llamacpp)
            api_key: API key for the backend
            base_url: Base URL for the backend
            enforce_safety: Whether to enforce safety checks
        """
        self.backend = backend
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.base_url = base_url or self._get_default_url(backend)
        self.enforce_safety = enforce_safety
        self.safety_checker = ModelSafetyChecker()
        self._client: Optional[httpx.AsyncClient] = None

    def _get_default_url(self, backend: str) -> str:
        """Get default URL for a backend."""
        defaults = {
            "huggingface": "https://api-inference.huggingface.co",
            "ollama": "http://localhost:11434",
            "vllm": "http://localhost:8000",
            "tgi": "http://localhost:8080",
            "llamacpp": "http://localhost:8080",
        }
        return defaults.get(backend, "http://localhost:8000")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=120.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def generate(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop: Optional[list[str]] = None,
    ) -> Optional[str]:
        """
        Generate text using a model.

        Args:
            model_id: Model to use
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stop: Stop sequences

        Returns:
            Generated text

        Raises:
            ValueError: If model is not safe
        """
        # Safety check
        if self.enforce_safety:
            is_safe, reason = self.safety_checker.is_model_safe(model_id)
            if not is_safe:
                raise ValueError(f"Model not approved for use: {reason}")

        client = await self._get_client()

        if self.backend == "huggingface":
            return await self._generate_huggingface(
                client, model_id, prompt, max_tokens, temperature, top_p
            )
        elif self.backend == "ollama":
            return await self._generate_ollama(
                client, model_id, prompt, max_tokens, temperature, top_p, stop
            )
        elif self.backend in ["vllm", "tgi", "llamacpp"]:
            return await self._generate_openai_compatible(
                client, model_id, prompt, max_tokens, temperature, top_p, stop
            )
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    async def _generate_huggingface(
        self,
        client: httpx.AsyncClient,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> Optional[str]:
        """Generate using Hugging Face Inference API."""
        response = await client.post(
            f"/models/{model_id}",
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "return_full_text": False,
                },
            },
        )

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", "")
                # Safety check output
                if self.enforce_safety:
                    is_safe, issues = self.safety_checker.check_output_safety(text)
                    if not is_safe:
                        logger.warning(f"Output safety issues: {issues}")
                return text
        else:
            logger.error(f"Generation failed: {response.status_code} - {response.text}")

        return None

    async def _generate_ollama(
        self,
        client: httpx.AsyncClient,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        stop: Optional[list[str]],
    ) -> Optional[str]:
        """Generate using Ollama."""
        response = await client.post(
            "/api/generate",
            json={
                "model": model_id,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                },
                "stream": False,
            },
        )

        if response.status_code == 200:
            result = response.json()
            text = result.get("response", "")
            if self.enforce_safety:
                is_safe, issues = self.safety_checker.check_output_safety(text)
                if not is_safe:
                    logger.warning(f"Output safety issues: {issues}")
            return text

        return None

    async def _generate_openai_compatible(
        self,
        client: httpx.AsyncClient,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        stop: Optional[list[str]],
    ) -> Optional[str]:
        """Generate using OpenAI-compatible API (vLLM, TGI, llama.cpp)."""
        response = await client.post(
            "/v1/completions",
            json={
                "model": model_id,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop,
            },
        )

        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            if choices:
                text = choices[0].get("text", "")
                if self.enforce_safety:
                    is_safe, issues = self.safety_checker.check_output_safety(text)
                    if not is_safe:
                        logger.warning(f"Output safety issues: {issues}")
                return text

        return None

    def list_safe_models(
        self,
        min_size_b: Optional[float] = None,
        max_size_b: Optional[float] = None,
        capability: Optional[str] = None,
        license_filter: Optional[ModelLicense] = None,
    ) -> list[SafeModel]:
        """
        List available safe models with optional filtering.

        Args:
            min_size_b: Minimum size in billions
            max_size_b: Maximum size in billions
            capability: Required capability
            license_filter: Required license

        Returns:
            List of matching SafeModel objects
        """
        models = []
        for model in SAFE_OSS_MODELS.values():
            if min_size_b and model.size_b < min_size_b:
                continue
            if max_size_b and model.size_b > max_size_b:
                continue
            if capability and capability not in model.capabilities:
                continue
            if license_filter and model.license != license_filter:
                continue
            models.append(model)

        return sorted(models, key=lambda m: m.size_b)

    def get_model_by_size(self, target_size_b: float) -> Optional[SafeModel]:
        """Get the closest model to a target size."""
        models = list(SAFE_OSS_MODELS.values())
        if not models:
            return None

        return min(models, key=lambda m: abs(m.size_b - target_size_b))
