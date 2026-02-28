"""Core extraction/classification/scoring step ports."""

from __future__ import annotations

from typing import Protocol

from penroselamarck.orchestrator.models import (
    ClassifiedGuidelineCandidate,
    ExtractedGuidelineCandidate,
    RepositoryTarget,
    ScoredGuidelineCandidate,
)


class TransientStepError(RuntimeError):
    """Raised when a workflow step can be retried safely."""


class Extractor(Protocol):
    """Extract guideline candidates for a repository target."""

    def extract(self, target: RepositoryTarget) -> list[ExtractedGuidelineCandidate]:
        """Return extracted candidates for one repository target."""


class Classifier(Protocol):
    """Convert extracted candidates into canonical normalized values."""

    def classify(
        self,
        target: RepositoryTarget,
        candidate: ExtractedGuidelineCandidate,
    ) -> ClassifiedGuidelineCandidate:
        """Return canonical classification for one extracted candidate."""


class Scorer(Protocol):
    """Score confidence and quality for a classified candidate."""

    def score(
        self,
        target: RepositoryTarget,
        extracted: ExtractedGuidelineCandidate,
        classified: ClassifiedGuidelineCandidate,
    ) -> ScoredGuidelineCandidate:
        """Return confidence and ranking scores for one classified candidate."""
