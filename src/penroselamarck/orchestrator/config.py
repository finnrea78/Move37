"""Environment configuration for orchestrator runtime scope."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OrchestratorScope:
    """Repository scan scope resolved from runtime environment variables."""

    organisations: list[str]
    repositories: list[str]
    enabled: bool

    @property
    def has_explicit_repositories(self) -> bool:
        return bool(self.repositories)


def load_scope_from_env() -> OrchestratorScope:
    organisations = _split_csv(os.environ.get("GITHUB_ORGANISATIONS", ""))
    repositories = _split_csv(os.environ.get("GITHUB_REPOSITORIES", ""))
    return OrchestratorScope(
        organisations=organisations,
        repositories=repositories,
        enabled=bool(organisations),
    )


def _split_csv(raw: str) -> list[str]:
    return [item for item in (token.strip() for token in raw.split(",")) if item]


@dataclass(frozen=True)
class OpenAISettings:
    """Runtime configuration for the OpenAI provider adapter."""

    api_key: str
    model: str
    temperature: float
    max_output_tokens: int
    base_url: str | None

    @classmethod
    def from_env(cls) -> OpenAISettings:
        api_key = (
            os.environ.get("OPENAI_API_KEY", "").strip() or os.environ.get("OPENAI_API", "").strip()
        )
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY (or OPENAI_API) is required for orchestrator LLM steps."
            )

        model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
        temperature_raw = os.environ.get("OPENAI_TEMPERATURE", "0.0").strip() or "0.0"
        max_tokens_raw = os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "1200").strip() or "1200"
        base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or None

        return cls(
            api_key=api_key,
            model=model,
            temperature=float(temperature_raw),
            max_output_tokens=int(max_tokens_raw),
            base_url=base_url,
        )


@dataclass(frozen=True)
class PromptVersionSettings:
    """Prompt version configuration for LLM workflow steps."""

    extraction: str
    classification: str
    scoring: str

    @classmethod
    def from_env(cls) -> PromptVersionSettings:
        default_version = os.environ.get("ORCHESTRATOR_PROMPT_VERSION", "v1").strip() or "v1"
        extraction = (
            os.environ.get("ORCHESTRATOR_EXTRACTION_PROMPT_VERSION", "").strip() or default_version
        )
        classification = (
            os.environ.get("ORCHESTRATOR_CLASSIFICATION_PROMPT_VERSION", "").strip()
            or default_version
        )
        scoring = (
            os.environ.get("ORCHESTRATOR_SCORING_PROMPT_VERSION", "").strip() or default_version
        )
        return cls(
            extraction=extraction,
            classification=classification,
            scoring=scoring,
        )


@dataclass(frozen=True)
class GitHubAPISettings:
    """Configuration for GitHub REST calls used by orchestrator adapters."""

    api_url: str
    token: str | None
    request_timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> GitHubAPISettings:
        token = os.environ.get("GITHUB_TOKEN", "").strip() or None
        api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        timeout_raw = os.environ.get("GITHUB_REQUEST_TIMEOUT_SECONDS", "30").strip() or "30"
        return cls(
            api_url=api_url,
            token=token,
            request_timeout_seconds=int(timeout_raw),
        )
