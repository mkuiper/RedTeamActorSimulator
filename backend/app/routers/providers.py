"""API endpoints for provider management."""

import logging

from fastapi import APIRouter

from app.providers import get_provider
from app.schemas.config import ProviderInfo, ProviderListResponse, ProviderModel

logger = logging.getLogger(__name__)

router = APIRouter()

PROVIDER_NAMES = ["openai", "anthropic", "google", "ollama"]

# Static model lists for when providers aren't configured
# This allows users to see all available options
# Updated: 2026-01-01
STATIC_MODELS = {
    "openai": [
        # Latest reasoning models
        {"id": "o3", "name": "o3", "description": "Advanced reasoning model with extended thinking", "context_window": 200000, "supports_thinking": True},
        {"id": "o3-mini", "name": "o3 Mini", "description": "Fast reasoning model", "context_window": 200000, "supports_thinking": True},
        {"id": "o1", "name": "o1", "description": "Reasoning model with chain-of-thought", "context_window": 200000, "supports_thinking": True},
        {"id": "o1-mini", "name": "o1 Mini", "description": "Efficient reasoning model", "context_window": 128000, "supports_thinking": True},
        # GPT-4 family
        {"id": "gpt-4o", "name": "GPT-4o", "description": "Most capable GPT-4 model with vision", "context_window": 128000, "supports_thinking": False},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and cost-effective", "context_window": 128000, "supports_thinking": False},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Previous generation with large context", "context_window": 128000, "supports_thinking": False},
    ],
    "anthropic": [
        # Claude 4.5 family (latest)
        {"id": "claude-opus-4-5-20251101", "name": "Claude Opus 4.5", "description": "Most capable Claude model", "context_window": 200000, "supports_thinking": True},
        {"id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "description": "Balanced performance and speed", "context_window": 200000, "supports_thinking": True},
        {"id": "claude-haiku-4-5-20250520", "name": "Claude Haiku 4.5", "description": "Fast and efficient", "context_window": 200000, "supports_thinking": True},
        # Claude 3.5 family
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Previous generation balanced model", "context_window": 200000, "supports_thinking": True},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "Fast previous generation", "context_window": 200000, "supports_thinking": True},
        # Claude 3 family
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Legacy most capable model", "context_window": 200000, "supports_thinking": True},
    ],
    "google": [
        # Gemini 2.0 family (latest)
        {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)", "description": "Latest fast Gemini model", "context_window": 1000000, "supports_thinking": False},
        {"id": "gemini-exp-1206", "name": "Gemini Experimental 1206", "description": "Experimental advanced model", "context_window": 2000000, "supports_thinking": False},
        # Gemini 1.5 family
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Most capable production Gemini model", "context_window": 2000000, "supports_thinking": False},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Fast and efficient", "context_window": 1000000, "supports_thinking": False},
        {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash 8B", "description": "Lightweight model", "context_window": 1000000, "supports_thinking": False},
    ],
    "ollama": [
        # Latest open models (2025/2026)
        {"id": "llama3.3:70b", "name": "Llama 3.3 70B", "description": "Meta's latest large open model", "context_window": 128000, "supports_thinking": False},
        {"id": "llama3.2:3b", "name": "Llama 3.2 3B", "description": "Efficient small model", "context_window": 128000, "supports_thinking": False},
        {"id": "llama3.1:70b", "name": "Llama 3.1 70B", "description": "Previous generation large model", "context_window": 128000, "supports_thinking": False},
        {"id": "llama3.1:8b", "name": "Llama 3.1 8B", "description": "Efficient mid-size model", "context_window": 128000, "supports_thinking": False},
        # Reasoning models
        {"id": "deepseek-r1:70b", "name": "DeepSeek R1 70B", "description": "Reasoning-focused open model", "context_window": 64000, "supports_thinking": True},
        {"id": "deepseek-r1:14b", "name": "DeepSeek R1 14B", "description": "Smaller reasoning model", "context_window": 64000, "supports_thinking": True},
        # Other quality models
        {"id": "qwen2.5:72b", "name": "Qwen 2.5 72B", "description": "Alibaba's latest model", "context_window": 128000, "supports_thinking": False},
        {"id": "mistral:7b", "name": "Mistral 7B", "description": "Fast open model", "context_window": 32000, "supports_thinking": False},
        {"id": "mixtral:8x7b", "name": "Mixtral 8x7B", "description": "MoE architecture", "context_window": 32000, "supports_thinking": False},
        {"id": "deepseek-coder:33b", "name": "DeepSeek Coder 33B", "description": "Code-focused model", "context_window": 16000, "supports_thinking": False},
    ],
}

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google AI",
    "ollama": "Ollama (Local)",
}


@router.get("", response_model=ProviderListResponse)
async def list_providers():
    """
    List all AI providers and their models.

    Models are always shown regardless of API key configuration.
    The 'available' field indicates if the provider is properly configured.
    """
    providers = []

    for provider_name in PROVIDER_NAMES:
        try:
            provider = get_provider(provider_name)
            is_available = provider.is_configured()

            # Always try to get models - use static list if not configured
            models = []
            if is_available:
                try:
                    model_infos = await provider.list_models()
                    models = [
                        ProviderModel(
                            id=m.id,
                            name=m.name,
                            description=m.description,
                            context_window=m.context_window,
                            supports_thinking=m.supports_thinking,
                        )
                        for m in model_infos
                    ]
                except Exception as e:
                    logger.warning(f"Failed to list models for {provider_name}: {e}")
                    # Fall back to static models
                    models = [
                        ProviderModel(**m)
                        for m in STATIC_MODELS.get(provider_name, [])
                    ]
            else:
                # Use static models when not configured
                models = [
                    ProviderModel(**m)
                    for m in STATIC_MODELS.get(provider_name, [])
                ]

            providers.append(
                ProviderInfo(
                    name=provider_name,
                    display_name=PROVIDER_DISPLAY_NAMES.get(provider_name, provider_name.title()),
                    available=is_available,
                    models=models,
                )
            )
        except Exception as e:
            logger.error(f"Error loading provider {provider_name}: {e}")
            # Still show provider with static models
            providers.append(
                ProviderInfo(
                    name=provider_name,
                    display_name=PROVIDER_DISPLAY_NAMES.get(provider_name, provider_name.title()),
                    available=False,
                    models=[ProviderModel(**m) for m in STATIC_MODELS.get(provider_name, [])],
                    error=str(e),
                )
            )

    return ProviderListResponse(providers=providers)


@router.post("/{provider_name}/test")
async def test_provider(provider_name: str):
    """Test connection to a specific provider."""
    try:
        provider = get_provider(provider_name)

        if not provider.is_configured():
            return {
                "status": "error",
                "provider": provider_name,
                "message": "Provider not configured (missing API key)",
            }

        success = await provider.test_connection()

        return {
            "status": "success" if success else "error",
            "provider": provider_name,
            "message": "Connection successful" if success else "Connection failed",
        }
    except ValueError as e:
        return {
            "status": "error",
            "provider": provider_name,
            "message": str(e),
        }
    except Exception as e:
        logger.error(f"Provider test error for {provider_name}: {e}")
        return {
            "status": "error",
            "provider": provider_name,
            "message": f"Connection test failed: {str(e)}",
        }


@router.get("/{provider_name}/models")
async def list_provider_models(provider_name: str):
    """List available models for a specific provider."""
    try:
        provider = get_provider(provider_name)

        if not provider.is_configured():
            return {
                "status": "error",
                "provider": provider_name,
                "models": [],
                "message": "Provider not configured",
            }

        models = await provider.list_models()

        return {
            "status": "success",
            "provider": provider_name,
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "context_window": m.context_window,
                    "supports_thinking": m.supports_thinking,
                }
                for m in models
            ],
        }
    except ValueError as e:
        return {
            "status": "error",
            "provider": provider_name,
            "models": [],
            "message": str(e),
        }
