"""OpenAI-backed scorer implementation."""

from __future__ import annotations

from opentelemetry import trace

from penroselamarck.orchestrator.config import OpenAISettings
from penroselamarck.orchestrator.models import (
    ClassifiedGuidelineCandidate,
    ExtractedGuidelineCandidate,
    RepositoryTarget,
    ScoredGuidelineCandidate,
)
from penroselamarck.orchestrator.ports import Scorer
from penroselamarck.orchestrator.prompts import load_prompt_set, render_user_prompt
from penroselamarck.orchestrator.providers.llm.openai.client import build_openai_chat_model
from penroselamarck.orchestrator.providers.llm.openai.schemas import ScoreResult

_TRACER = trace.get_tracer("penroselamarck.orchestrator.openai")


class OpenAIScorer(Scorer):
    """Scores confidence and quality for classified guideline candidates."""

    def __init__(self, settings: OpenAISettings, prompt_version: str = "v1") -> None:
        self._prompt = load_prompt_set(step="scoring", version=prompt_version)
        llm = build_openai_chat_model(settings)
        self._structured_llm = llm.with_structured_output(ScoreResult)

    def score(
        self,
        target: RepositoryTarget,
        extracted: ExtractedGuidelineCandidate,
        classified: ClassifiedGuidelineCandidate,
    ) -> ScoredGuidelineCandidate:
        """Score one candidate using the configured scoring prompt version."""
        with _TRACER.start_as_current_span(
            "orchestrator.score.llm_call",
            attributes={
                "penroselamarck.repository": f"{target.owner}/{target.name}",
                "penroselamarck.file_path": extracted.file_path,
                "penroselamarck.prompt.step": self._prompt.step,
                "penroselamarck.prompt.version": self._prompt.version,
            },
        ):
            user_prompt = render_user_prompt(
                self._prompt.user_template,
                {
                    "repository": f"{target.owner}/{target.name}",
                    "file_path": extracted.file_path,
                    "original_title": extracted.title,
                    "original_value": extracted.value,
                    "canonical_title": classified.canonical_title,
                    "canonical_value": classified.canonical_value,
                    "class_names": ", ".join(classified.class_names),
                },
            )
            result = self._structured_llm.invoke([
                ("system", self._prompt.system_prompt),
                ("user", user_prompt),
            ])

        return ScoredGuidelineCandidate(
            confidence_score=result.confidence_score,
            score=result.score,
        )
