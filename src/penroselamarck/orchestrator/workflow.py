"""Extract -> classify -> score -> review workflow execution."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from penroselamarck.orchestrator.models import (
    ExtractedGuidelineCandidate,
    RepositoryTarget,
    WorkflowItemResult,
    WorkflowRetryPolicy,
    WorkflowRunSummary,
    WorkflowThresholds,
)
from penroselamarck.orchestrator.ports import (
    Classifier,
    Extractor,
    Scorer,
    TransientStepError,
    WorkflowStore,
)

_T = TypeVar("_T")


class OrchestratorWorkflow:
    """Runs the guideline workflow with retries and review routing."""

    def __init__(
        self,
        extractor: Extractor,
        classifier: Classifier,
        scorer: Scorer,
        store: WorkflowStore,
        thresholds: WorkflowThresholds | None = None,
        retries: WorkflowRetryPolicy | None = None,
    ) -> None:
        self._extractor = extractor
        self._classifier = classifier
        self._scorer = scorer
        self._store = store
        self._thresholds = thresholds or WorkflowThresholds()
        self._retries = retries or WorkflowRetryPolicy()

    def run_repository(self, target: RepositoryTarget) -> WorkflowRunSummary:
        summary = WorkflowRunSummary(repository=f"{target.owner}/{target.name}")

        try:
            candidates, extract_attempts = self._run_with_retries(
                lambda: self._extractor.extract(target),
                max_retries=self._retries.extract_retries,
            )
        except Exception as exc:
            summary.failed = 1
            summary.items.append(
                WorkflowItemResult(
                    file_path="<repository>",
                    guideline_uid=None,
                    status="failed",
                    needs_review=False,
                    review_uid=None,
                    retry_counts={"extract": self._retries.extract_retries + 1},
                    error=str(exc),
                )
            )
            return summary

        for candidate in candidates:
            summary.processed += 1
            item_result = self._run_candidate(target, candidate, extract_attempts)
            summary.items.append(item_result)
            if item_result.status == "failed":
                summary.failed += 1
                continue
            summary.persisted += 1
            if item_result.needs_review:
                summary.reviews_created += 1

        return summary

    def _run_candidate(
        self,
        target: RepositoryTarget,
        candidate: ExtractedGuidelineCandidate,
        extract_attempts: int,
    ) -> WorkflowItemResult:
        retry_counts = {"extract": extract_attempts, "classify": 0, "score": 0}

        try:
            classified, classify_attempts = self._run_with_retries(
                lambda: self._classifier.classify(target, candidate),
                max_retries=self._retries.classify_retries,
            )
            retry_counts["classify"] = classify_attempts

            scored, score_attempts = self._run_with_retries(
                lambda: self._scorer.score(target, candidate, classified),
                max_retries=self._retries.score_retries,
            )
            retry_counts["score"] = score_attempts

            needs_review = (
                scored.confidence_score < self._thresholds.review_confidence_threshold
                or scored.score < self._thresholds.review_score_threshold
            )
            status = "draft" if needs_review else "active"
            persisted = self._store.persist_guideline(
                target=target,
                extracted=candidate,
                classified=classified,
                scored=scored,
                status=status,
            )

            review_uid = None
            if needs_review:
                notes = (
                    "Low-confidence autonomous decision. "
                    f"confidence={scored.confidence_score:.5f}, score={scored.score:.5f}"
                )
                review_uid = self._store.create_guideline_review(
                    guideline_id=persisted.guideline_id,
                    notes=notes,
                )

            return WorkflowItemResult(
                file_path=candidate.file_path,
                guideline_uid=persisted.guideline_uid,
                status="completed",
                needs_review=needs_review,
                review_uid=review_uid,
                retry_counts=retry_counts,
            )
        except Exception as exc:
            return WorkflowItemResult(
                file_path=candidate.file_path,
                guideline_uid=None,
                status="failed",
                needs_review=False,
                review_uid=None,
                retry_counts=retry_counts,
                error=str(exc),
            )

    def _run_with_retries(
        self,
        action: Callable[[], _T],
        max_retries: int,
    ) -> tuple[_T, int]:
        attempts = 0
        while True:
            attempts += 1
            try:
                return action(), attempts
            except TransientStepError:
                if attempts > max_retries:
                    raise
