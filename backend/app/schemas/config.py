"""Configuration-related Pydantic schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for a specific model."""

    provider: str = Field(..., description="Provider name (openai, anthropic, google, ollama)")
    model: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)


class SimulationConfig(BaseModel):
    """Full simulation configuration."""

    max_turns: int = Field(default=20, ge=1, le=100)
    sneaky_mode: bool = False
    actor_config: ModelConfig
    assessor_config: ModelConfig
    subject_config: ModelConfig


class ProviderModel(BaseModel):
    """Information about a specific model."""

    id: str
    name: str
    description: Optional[str] = None
    context_window: Optional[int] = None
    supports_thinking: bool = False


class ProviderInfo(BaseModel):
    """Information about an AI provider."""

    name: str
    display_name: str
    available: bool
    models: List[ProviderModel] = []
    error: Optional[str] = None


class ProviderListResponse(BaseModel):
    """Response for listing all providers."""

    providers: List[ProviderInfo]
