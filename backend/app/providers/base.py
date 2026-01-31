"""Base provider interface for AI model adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ProviderResponse:
    """Standardized response from any provider."""

    content: str
    thinking: Optional[str] = None  # Chain-of-thought if available
    model: str = ""
    usage: Optional[dict] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[dict] = None


@dataclass
class ModelInfo:
    """Information about a specific model."""

    id: str
    name: str
    description: Optional[str] = None
    context_window: Optional[int] = None
    supports_thinking: bool = False


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    name: str = "base"
    display_name: str = "Base Provider"

    @abstractmethod
    async def generate(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        request_thinking: bool = False,
    ) -> ProviderResponse:
        """
        Generate a response from the model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            request_thinking: Whether to request chain-of-thought

        Returns:
            ProviderResponse with generated content
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the provider is properly configured and accessible."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider has necessary credentials configured."""
        pass
