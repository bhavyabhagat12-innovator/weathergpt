"""
LLM Provider Factory.
Instantiates and caches the configured model provider.
"""

from app.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.providers.fallback import FallbackAdvisoryProvider
from app.llm.providers.gemini import GeminiLLMProvider
from app.llm.providers.openai_ollama import OpenAIOllamaProvider


def get_llm_provider() -> BaseLLMProvider:
    """Returns the configured LLM provider instance."""
    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "gemini":
        return GeminiLLMProvider()
    elif provider_name == "openai":
        return OpenAIOllamaProvider(is_ollama=False)
    elif provider_name == "ollama":
        return OpenAIOllamaProvider(is_ollama=True)
    else:
        return FallbackAdvisoryProvider()
