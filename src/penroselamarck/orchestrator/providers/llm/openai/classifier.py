"""OpenAI-backed classifier implementation."""

from __future__ import annotations

from opentelemetry import trace

from penroselamarck.orchestrator.config import OpenAISettings
from penroselamarck.orchestrator.models import (
    ClassifiedGuidelineCandidate,
    ExtractedGuidelineCandidate,
    RepositoryTarget,
)
from penroselamarck.orchestrator.ports import Classifier
from penroselamarck.orchestrator.prompts import load_prompt_set, render_user_prompt
from penroselamarck.orchestrator.providers.llm.openai.client import build_openai_chat_model
from penroselamarck.orchestrator.providers.llm.openai.schemas import ClassificationResult
from penroselamarck.orchestrator.providers.llm.openai.utils import normalize_value_key

_TRACER = trace.get_tracer("penroselamarck.orchestrator.openai")


class OpenAIClassifier(Classifier):
    """Normalizes extracted guideline candidates into canonical forms."""

    def __init__(self, settings: OpenAISettings, prompt_version: str = "v1") -> None:
        self._prompt = load_prompt_set(step="classification", version=prompt_version)
        llm = build_openai_chat_model(settings)
        self._structured_llm = llm.with_structured_output(ClassificationResult)

    def classify(
        self,
        target: RepositoryTarget,
        candidate: ExtractedGuidelineCandidate,
    ) -> ClassifiedGuidelineCandidate:
        """Classify one extracted candidate using a structured LLM call."""
        with _TRACER.start_as_current_span(
            "orchestrator.classify.llm_call",
            attributes={
                "penroselamarck.repository": f"{target.owner}/{target.name}",
                "penroselamarck.file_path": candidate.file_path,
                "penroselamarck.prompt.step": self._prompt.step,
                "penroselamarck.prompt.version": self._prompt.version,
            },
        ):
            user_prompt = render_user_prompt(
                self._prompt.user_template,
                {
                    "repository": f"{target.owner}/{target.name}",
                    "file_path": candidate.file_path,
                    "title": candidate.title,
                    "value": candidate.value,
                    "rationale": candidate.rationale or "",
                    "existing_classes": ", ".join(candidate.class_names),
                },
            )
            result = self._structured_llm.invoke([
                ("system", self._prompt.system_prompt),
                ("user", user_prompt),
            ])

        value_key = normalize_value_key(result.value_key) or normalize_value_key(
            result.canonical_value
        )
        return ClassifiedGuidelineCandidate(
            canonical_title=result.canonical_title.strip(),
            canonical_value=result.canonical_value.strip(),
            value_key=value_key or "unspecified",
            class_names=[name.strip() for name in result.class_names if name.strip()],
        )
