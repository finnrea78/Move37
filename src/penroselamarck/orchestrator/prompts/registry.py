"""Prompt registry for versioned orchestrator prompt assets.

The orchestrator uses three logical steps backed by prompts:

- ``extraction``
- ``classification``
- ``scoring``

Each step can have multiple prompt versions (for example ``v1``, ``v2``), and
each version contains:

- ``system.txt``: stable instruction framing
- ``user.txt``: runtime-templated request payload
- ``schema.json``: JSON schema snapshot for structured output expectations

The schema file is primarily documentation and traceability metadata. Runtime
validation is enforced in provider code via Pydantic structured-output models.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"
_SUPPORTED_STEPS = frozenset({"extraction", "classification", "scoring"})


@dataclass(frozen=True)
class PromptSet:
    """Fully loaded prompt assets for one step/version pair."""

    step: str
    version: str
    system_prompt: str
    user_template: str
    schema_json: str


class PromptRegistry:
    """Resolves and loads prompt assets from the filesystem."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or _TEMPLATE_ROOT

    def load(self, step: str, version: str) -> PromptSet:
        """Load ``system.txt``, ``user.txt``, and ``schema.json`` for a step."""
        step_normalized = (step or "").strip().lower()
        version_normalized = (version or "").strip().lower()

        if step_normalized not in _SUPPORTED_STEPS:
            supported = ", ".join(sorted(_SUPPORTED_STEPS))
            raise ValueError(f"Unsupported prompt step '{step}'. Supported steps: {supported}.")
        if not version_normalized:
            raise ValueError("Prompt version cannot be empty.")

        base_path = self._root / step_normalized / version_normalized
        system_prompt = _read_text(base_path / "system.txt")
        user_template = _read_text(base_path / "user.txt")
        schema_json = _read_text(base_path / "schema.json")
        return PromptSet(
            step=step_normalized,
            version=version_normalized,
            system_prompt=system_prompt,
            user_template=user_template,
            schema_json=schema_json,
        )


@lru_cache(maxsize=16)
def load_prompt_set(step: str, version: str = "v1") -> PromptSet:
    """Load and cache prompt assets for one step/version pair."""
    return PromptRegistry().load(step=step, version=version)


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt asset not found: {path}")
    return path.read_text(encoding="utf-8").strip()
