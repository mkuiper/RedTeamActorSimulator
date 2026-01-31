"""Google AI (Gemini) provider adapter."""

import logging
from typing import List, Optional

import google.generativeai as genai

from app.config import get_settings
from app.providers.base import BaseProvider, ModelInfo, ProviderResponse

logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""

    name = "google"
    display_name = "Google AI"

    def __init__(self):
        self.settings = get_settings()
        if self.is_configured():
            genai.configure(api_key=self.settings.google_api_key)

    def is_configured(self) -> bool:
        return bool(self.settings.google_api_key)

    async def generate(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        request_thinking: bool = False,
    ) -> ProviderResponse:
        if not self.is_configured():
            raise RuntimeError("Google AI provider not configured")

        try:
            # Initialize the model
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=system_prompt if system_prompt else None,
            )

            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [msg["content"]],
                })

            # Generate response
            response = await model_instance.generate_content_async(
                gemini_messages,
            )

            return ProviderResponse(
                content=response.text,
                thinking=None,  # Gemini doesn't expose thinking
                model=model,
                usage={
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                } if response.usage_metadata else None,
                finish_reason=str(response.candidates[0].finish_reason) if response.candidates else None,
            )
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
            raise

    async def list_models(self) -> List[ModelInfo]:
        """List available Google models."""
        return [
            ModelInfo(
                id="gemini-3-pro-preview",
                name="Gemini 3 Pro (Preview)",
                description="Most advanced reasoning Gemini model for complex problems",
                context_window=1000000,
            ),
            ModelInfo(
                id="gemini-3-flash-preview",
                name="Gemini 3 Flash (Preview)",
                description="Pro-level intelligence at Flash speed - frontier intelligence with agentic vision",
                context_window=1000000,
            ),
            ModelInfo(
                id="gemini-2.0-flash-thinking-exp-01-21",
                name="Gemini 2.0 Flash Thinking",
                description="Gemini 2.0 with extended reasoning",
                context_window=1000000,
            ),
            ModelInfo(
                id="gemini-2.0-flash-exp",
                name="Gemini 2.0 Flash",
                description="Fast Gemini 2.0 model",
                context_window=1000000,
            ),
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                description="Most capable Gemini 1.5 model",
                context_window=2000000,
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                description="Fast and efficient Gemini 1.5",
                context_window=1000000,
            ),
        ]

    async def test_connection(self) -> bool:
        """Test Google AI connection."""
        if not self.is_configured():
            return False

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            await model.generate_content_async("Hi")
            return True
        except Exception as e:
            logger.error(f"Google AI connection test failed: {e}")
            return False
