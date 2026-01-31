"""OpenAI provider adapter."""

import logging
from typing import List, Optional

from openai import AsyncOpenAI

from app.config import get_settings
from app.providers.base import BaseProvider, ModelInfo, ProviderResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI models (GPT-4, GPT-3.5, etc.)."""

    name = "openai"
    display_name = "OpenAI"

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.is_configured():
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    def is_configured(self) -> bool:
        return bool(self.settings.openai_api_key)

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
            raise RuntimeError("OpenAI provider not configured")

        # Prepend system prompt if provided
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            choice = response.choices[0]
            return ProviderResponse(
                content=choice.message.content or "",
                thinking=None,  # OpenAI doesn't expose thinking
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
                finish_reason=choice.finish_reason,
                raw_response=response.model_dump(),
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def list_models(self) -> List[ModelInfo]:
        """List available OpenAI models."""
        # Return commonly used models
        return [
            # GPT-5 Family (Latest)
            ModelInfo(
                id="gpt-5.2",
                name="GPT-5.2",
                description="Flagship reasoning model with variable effort levels",
                context_window=200000,
            ),
            ModelInfo(
                id="gpt-5",
                name="GPT-5",
                description="Developer-focused model for coding and agents",
                context_window=200000,
            ),
            ModelInfo(
                id="gpt-5-mini",
                name="GPT-5 Mini",
                description="Smaller, faster GPT-5 variant",
                context_window=128000,
            ),
            # O-Series Reasoning Models
            ModelInfo(
                id="o3-pro",
                name="o3-pro",
                description="Most advanced reasoning model",
                context_window=200000,
            ),
            ModelInfo(
                id="o3",
                name="o3",
                description="Advanced reasoning model",
                context_window=200000,
            ),
            ModelInfo(
                id="o3-mini",
                name="o3-mini",
                description="Efficient reasoning model",
                context_window=128000,
            ),
            ModelInfo(
                id="o1",
                name="o1",
                description="Advanced reasoning model with extended thinking",
                context_window=200000,
            ),
            ModelInfo(
                id="o1-mini",
                name="o1-mini",
                description="Faster reasoning model",
                context_window=128000,
            ),
            # GPT-4 Family
            ModelInfo(
                id="gpt-4.5",
                name="GPT-4.5",
                description="High EQ model, excellent at creative tasks and agentic planning",
                context_window=128000,
            ),
            ModelInfo(
                id="gpt-4.1",
                name="GPT-4.1",
                description="Specialized for coding tasks and precise instruction following",
                context_window=128000,
            ),
            ModelInfo(
                id="gpt-4o",
                name="GPT-4o",
                description="Multimodal model with vision and audio support",
                context_window=128000,
            ),
            ModelInfo(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                description="Fast and cost-effective",
                context_window=128000,
            ),
        ]

    async def test_connection(self) -> bool:
        """Test OpenAI connection."""
        if not self.client:
            return False

        try:
            # Make a minimal API call
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
