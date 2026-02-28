"""Workflow policy and summary dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WorkflowThresholds:
    """Cutoffs that route persisted candidates to review."""

    review_confidence_threshold: float = 0.65
    review_score_threshold: float = 0.50


@dataclass(frozen=True)
class WorkflowRetryPolicy:
    """Per-step retry limits for transient workflow failures."""

    extract_retries: int = 2
    classify_retries: int = 1
    score_retries: int = 1


@dataclass(frozen=True)
class WorkflowItemResult:
    """Final processing outcome for one extracted candidate."""

    file_path: str
    guideline_uid: str | None
    status: str
    needs_review: bool
    review_uid: str | None
    retry_counts: dict[str, int]
    error: str | None = None


@dataclass
class WorkflowRunSummary:
    """Repository-level aggregate counters and item-level outcomes."""

    repository: str
    processed: int = 0
    persisted: int = 0
    reviews_created: int = 0
    failed: int = 0
    items: list[WorkflowItemResult] = field(default_factory=list)
