"""OpenAI Chat model construction utilities.

This module is intentionally small and isolated so future provider-specific
configuration (timeouts, retries, headers, rate controls) can be centralized.
"""

from __future__ import annotations

from penroselamarck.orchestrator.config import OpenAISettings


def build_openai_chat_model(settings: OpenAISettings):
    """Build a configured ``langchain_openai.ChatOpenAI`` instance."""
    from langchain_openai import ChatOpenAI

    kwargs: dict[str, object] = {
        "model": settings.model,
        "api_key": settings.api_key,
        "temperature": settings.temperature,
        "max_tokens": settings.max_output_tokens,
    }
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    return ChatOpenAI(**kwargs)
