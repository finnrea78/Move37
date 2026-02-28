"""Prompt management package for orchestrator LLM steps.

This package provides three capabilities:

1. Versioned prompt assets stored on disk under ``prompts/templates``.
2. A registry that resolves prompt versions per workflow step.
3. A renderer that safely fills template variables at runtime.

Keeping prompts in files decouples prompt iteration from provider code and
supports a future prompt-evaluation and fine-tuning workflow.
"""

from penroselamarck.orchestrator.prompts.registry import (
    PromptRegistry,
    PromptSet,
    load_prompt_set,
)
from penroselamarck.orchestrator.prompts.renderer import render_user_prompt

__all__ = [
    "PromptRegistry",
    "PromptSet",
    "load_prompt_set",
    "render_user_prompt",
]
