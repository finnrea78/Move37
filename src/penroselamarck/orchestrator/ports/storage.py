"""Persistence port for workflow outputs and review lifecycle."""

from __future__ import annotations

from typing import Protocol

from penroselamarck.orchestrator.models import (
    ClassifiedGuidelineCandidate,
    ExtractedGuidelineCandidate,
    PersistedGuideline,
    RepositoryTarget,
    ScoredGuidelineCandidate,
)


class WorkflowStore(Protocol):
    """Persistence boundary used by workflow engines."""

    def persist_guideline(
        self,
        target: RepositoryTarget,
        extracted: ExtractedGuidelineCandidate,
        classified: ClassifiedGuidelineCandidate,
        scored: ScoredGuidelineCandidate,
        status: str,
    ) -> PersistedGuideline:
        """Persist guideline graph entities and return guideline identity."""

    def create_guideline_review(self, guideline_id: int, notes: str) -> str:
        """Create (or reuse) a human review record for one guideline row."""

    def resolve_guideline_review(self, review_uid: str, action: str, notes: str) -> None:
        """Resolve one review record after HITL decision."""

    def set_guideline_status(self, guideline_id: int, status: str) -> None:
        """Set guideline lifecycle status after review outcome."""
