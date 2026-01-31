"""Anthropic provider adapter."""

import logging
from typing import List, Optional

from anthropic import AsyncAnthropic

from app.config import get_settings
from app.providers.base import BaseProvider, ModelInfo, ProviderResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models."""

    name = "anthropic"
    display_name = "Anthropic"

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.is_configured():
            self.client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

    def is_configured(self) -> bool:
        return bool(self.settings.anthropic_api_key)

    async def generate(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        request_thinking: bool = False,
    ) -> ProviderResponse:
        if not self.client:
            raise RuntimeError("Anthropic provider not configured")

        try:
            # Build request parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
            }

            if system_prompt:
                params["system"] = system_prompt

            # Handle extended thinking for supported models
            thinking_content = None
            if request_thinking and "claude-3" in model:
                # Enable extended thinking with streaming budget
                params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": 10000,
                }
                params["temperature"] = 1  # Required for thinking
            else:
                params["temperature"] = temperature

            response = await self.client.messages.create(**params)

            # Extract content and thinking
            content = ""
            for block in response.content:
                if block.type == "text":
                    content = block.text
                elif block.type == "thinking":
                    thinking_content = block.thinking

            return ProviderResponse(
                content=content,
                thinking=thinking_content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                } if response.usage else None,
                finish_reason=response.stop_reason,
                raw_response=response.model_dump(),
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def list_models(self) -> List[ModelInfo]:
        """List available Anthropic models."""
        return [
            ModelInfo(
                id="claude-opus-4-5-20251101",
                name="Claude Opus 4.5",
                description="Most capable Claude model with extended thinking",
                context_window=200000,
                supports_thinking=True,
            ),
            ModelInfo(
                id="claude-sonnet-4-5-20250929",
                name="Claude Sonnet 4.5",
                description="Balanced performance and speed with extended thinking",
                context_window=200000,
                supports_thinking=True,
            ),
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="Previous generation balanced model",
                context_window=200000,
                supports_thinking=True,
            ),
            ModelInfo(
                id="claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                description="Fast and efficient",
                context_window=200000,
                supports_thinking=True,
            ),
        ]

    async def test_connection(self) -> bool:
        """Test Anthropic connection."""
        if not self.client:
            return False

        try:
            # Make a minimal API call
            await self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            return False
