"""Core dataclasses used by orchestrator steps and adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryTarget:
    """Immutable repository snapshot used as workflow input."""

    owner: str
    name: str
    repo_url: str
    default_branch: str
    head_sha: str


@dataclass(frozen=True)
class ExtractedGuidelineCandidate:
    """Raw guideline candidate extracted from one repository file."""

    file_path: str
    file_url: str
    title: str
    value: str
    rationale: str | None
    class_names: list[str]
    source_hash: str | None = None
    rationale_type: str | None = None


@dataclass(frozen=True)
class ClassifiedGuidelineCandidate:
    """Canonicalized guideline title/value and assigned classes."""

    canonical_title: str
    canonical_value: str
    value_key: str
    class_names: list[str]


@dataclass(frozen=True)
class ScoredGuidelineCandidate:
    """Model confidence and quality score for one classified candidate."""

    confidence_score: float
    score: float


@dataclass(frozen=True)
class PersistedGuideline:
    """Database identity returned after persistence."""

    guideline_id: int
    guideline_uid: str
    status: str
