"""Ollama provider adapter for local models."""

import logging
from typing import List, Optional

import httpx
from ollama import AsyncClient

from app.config import get_settings
from app.providers.base import BaseProvider, ModelInfo, ProviderResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """Provider for Ollama local models."""

    name = "ollama"
    display_name = "Ollama (Local)"

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncClient(host=self.settings.ollama_base_url)

    def is_configured(self) -> bool:
        # Ollama doesn't need API key, always "configured"
        return True

    async def generate(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        request_thinking: bool = False,
    ) -> ProviderResponse:
        try:
            # Prepend system message if provided
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            response = await self.client.chat(
                model=model,
                messages=full_messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            return ProviderResponse(
                content=response["message"]["content"],
                thinking=None,  # Ollama doesn't expose thinking
                model=model,
                usage={
                    "prompt_tokens": response.get("prompt_eval_count", 0),
                    "completion_tokens": response.get("eval_count", 0),
                    "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
                },
                finish_reason="stop",
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def list_models(self) -> List[ModelInfo]:
        """List available Ollama models."""
        try:
            response = await self.client.list()
            models = []
            for model in response.get("models", []):
                name = model.get("name", "")
                models.append(ModelInfo(
                    id=name,
                    name=name,
                    description=f"Local model: {name}",
                    context_window=None,  # Varies by model
                ))
            return models
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    async def test_connection(self) -> bool:
        """Test Ollama connection."""
        try:
            # Try to list models as a connection test
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.ollama_base_url}/api/tags",
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
