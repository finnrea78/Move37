"""Structured-output schemas for OpenAI-backed orchestrator steps.

These Pydantic models define the runtime contract expected from LLM structured
outputs. Prompt JSON schemas in ``orchestrator/prompts/templates`` mirror these
shapes for versioning and evaluation traceability.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractionItem(BaseModel):
    """One extracted guideline candidate from a repository document."""

    title: str
    value: str
    rationale: str | None = None
    class_names: list[str] = Field(default_factory=list)
    rationale_type: str | None = None


class ExtractionResult(BaseModel):
    """Collection of extracted guideline items for one source file."""

    items: list[ExtractionItem] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    """Canonical representation for one extracted candidate."""

    canonical_title: str
    canonical_value: str
    value_key: str
    class_names: list[str] = Field(default_factory=list)


class ScoreResult(BaseModel):
    """Confidence and quality scores for one canonical candidate."""

    confidence_score: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)
