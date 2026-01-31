"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=[str(ROOT_ENV_PATH), str(BACKEND_ENV_PATH)],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # AI Provider API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Database
    database_url: str = "sqlite+aiosqlite:///./redteam_simulator.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Simulation defaults
    default_max_turns: int = 20
    default_actor_model: str = "anthropic:claude-3-5-sonnet-20241022"
    default_assessor_model: str = "anthropic:claude-3-5-sonnet-20241022"

    # Logging
    log_level: str = "INFO"

    def has_provider(self, provider: str) -> bool:
        """Check if a provider is configured with API key."""
        provider_keys = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "ollama": True,  # Ollama doesn't need API key
        }
        key = provider_keys.get(provider.lower())
        return bool(key)

    def get_available_providers(self) -> List[str]:
        """Get list of configured providers."""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_api_key:
            providers.append("google")
        # Ollama is always available (local)
        providers.append("ollama")
        return providers


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
