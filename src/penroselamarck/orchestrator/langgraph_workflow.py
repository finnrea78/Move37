"""LangGraph multi-node workflow with HITL interrupts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from typing import TypedDict

from penroselamarck.orchestrator.models import (
    ClassifiedGuidelineCandidate,
    ExtractedGuidelineCandidate,
    PersistedGuideline,
    RepositoryTarget,
    ScoredGuidelineCandidate,
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


class ReviewDecision(TypedDict, total=False):
    action: str
    notes: str


class WorkflowGraphState(TypedDict, total=False):
    target: RepositoryTarget
    extracted: list[ExtractedGuidelineCandidate]
    candidate_index: int
    current_candidate: ExtractedGuidelineCandidate | None
    classified: ClassifiedGuidelineCandidate | None
    scored: ScoredGuidelineCandidate | None
    persisted: PersistedGuideline | None
    needs_review: bool
    review_uid: str | None
    summary: WorkflowRunSummary
    retry_counts: dict[str, int]
    continue_to_next: bool


class LangGraphGuidelineWorkflow:
    """Concrete LangGraph workflow for extract -> classify -> score -> review."""

    def __init__(
        self,
        extractor: Extractor,
        classifier: Classifier,
        scorer: Scorer,
        store: WorkflowStore,
        thresholds: WorkflowThresholds | None = None,
        retries: WorkflowRetryPolicy | None = None,
        hitl_resolver: Callable[[dict], ReviewDecision] | None = None,
    ) -> None:
        self._extractor = extractor
        self._classifier = classifier
        self._scorer = scorer
        self._store = store
        self._thresholds = thresholds or WorkflowThresholds()
        self._retries = retries or WorkflowRetryPolicy()
        self._hitl_resolver = hitl_resolver

    def compile(self, checkpointer=None):
        """Compile a reusable repository workflow graph."""
        try:
            from langgraph.graph import END, START, StateGraph
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "LangGraph is not installed. Install orchestrator requirements first."
            ) from exc

        graph = StateGraph(WorkflowGraphState)
        graph.add_node("extract", self._extract_node)
        graph.add_node("next_candidate", self._next_candidate_node)
        graph.add_node("classify", self._classify_node)
        graph.add_node("score", self._score_node)
        graph.add_node("persist", self._persist_node)
        graph.add_node("review", self._review_node)

        graph.add_edge(START, "extract")
        graph.add_edge("extract", "next_candidate")
        graph.add_conditional_edges(
            "next_candidate",
            self._route_after_next_candidate,
            {"classify": "classify", "end": END},
        )
        graph.add_conditional_edges(
            "classify",
            self._route_after_classify,
            {"score": "score", "next": "next_candidate"},
        )
        graph.add_conditional_edges(
            "score",
            self._route_after_score,
            {"persist": "persist", "next": "next_candidate"},
        )
        graph.add_conditional_edges(
            "persist",
            self._route_after_persist,
            {"review": "review", "next": "next_candidate"},
        )
        graph.add_edge("review", "next_candidate")
        return graph.compile(checkpointer=checkpointer)

    def _extract_node(self, state: WorkflowGraphState) -> dict:
        target = state["target"]
        summary = WorkflowRunSummary(repository=f"{target.owner}/{target.name}")
        try:
            extracted, extract_attempts = self._run_with_retries(
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
            return {
                "summary": summary,
                "extracted": [],
                "candidate_index": 0,
                "current_candidate": None,
                "continue_to_next": False,
            }
        return {
            "summary": summary,
            "extracted": extracted,
            "candidate_index": 0,
            "current_candidate": None,
            "retry_counts": {"extract": extract_attempts, "classify": 0, "score": 0},
            "continue_to_next": True,
        }

    def _next_candidate_node(self, state: WorkflowGraphState) -> dict:
        extracted = state.get("extracted", [])
        index = state.get("candidate_index", 0)
        summary = state["summary"]
        if index >= len(extracted):
            return {"current_candidate": None, "continue_to_next": False, "summary": summary}

        candidate = extracted[index]
        summary.processed += 1
        retry_counts = dict(state.get("retry_counts", {}))
        retry_counts.setdefault("extract", 1)
        retry_counts["classify"] = 0
        retry_counts["score"] = 0
        return {
            "current_candidate": candidate,
            "classified": None,
            "scored": None,
            "persisted": None,
            "needs_review": False,
            "review_uid": None,
            "retry_counts": retry_counts,
            "continue_to_next": True,
            "summary": summary,
        }

    def _classify_node(self, state: WorkflowGraphState) -> dict:
        summary = state["summary"]
        target = state["target"]
        candidate = state["current_candidate"]
        retry_counts = dict(state["retry_counts"])

        try:
            classified, attempts = self._run_with_retries(
                lambda: self._classifier.classify(target, candidate),
                max_retries=self._retries.classify_retries,
            )
            retry_counts["classify"] = attempts
            return {
                "classified": classified,
                "retry_counts": retry_counts,
                "continue_to_next": False,
                "summary": summary,
            }
        except Exception as exc:
            summary.failed += 1
            summary.items.append(
                WorkflowItemResult(
                    file_path=candidate.file_path,
                    guideline_uid=None,
                    status="failed",
                    needs_review=False,
                    review_uid=None,
                    retry_counts=retry_counts,
                    error=str(exc),
                )
            )
            return {
                "continue_to_next": True,
                "candidate_index": state["candidate_index"] + 1,
                "summary": summary,
            }

    def _score_node(self, state: WorkflowGraphState) -> dict:
        summary = state["summary"]
        target = state["target"]
        candidate = state["current_candidate"]
        classified = state["classified"]
        retry_counts = dict(state["retry_counts"])

        try:
            scored, attempts = self._run_with_retries(
                lambda: self._scorer.score(target, candidate, classified),
                max_retries=self._retries.score_retries,
            )
            retry_counts["score"] = attempts
            return {
                "scored": scored,
                "retry_counts": retry_counts,
                "continue_to_next": False,
                "summary": summary,
            }
        except Exception as exc:
            summary.failed += 1
            summary.items.append(
                WorkflowItemResult(
                    file_path=candidate.file_path,
                    guideline_uid=None,
                    status="failed",
                    needs_review=False,
                    review_uid=None,
                    retry_counts=retry_counts,
                    error=str(exc),
                )
            )
            return {
                "continue_to_next": True,
                "candidate_index": state["candidate_index"] + 1,
                "summary": summary,
            }

    def _persist_node(self, state: WorkflowGraphState) -> dict:
        summary = state["summary"]
        target = state["target"]
        candidate = state["current_candidate"]
        classified = state["classified"]
        scored = state["scored"]
        retry_counts = dict(state["retry_counts"])
        needs_review = (
            scored.confidence_score < self._thresholds.review_confidence_threshold
            or scored.score < self._thresholds.review_score_threshold
        )
        status = "draft" if needs_review else "active"

        try:
            persisted = self._store.persist_guideline(
                target=target,
                extracted=candidate,
                classified=classified,
                scored=scored,
                status=status,
            )
        except Exception as exc:
            summary.failed += 1
            summary.items.append(
                WorkflowItemResult(
                    file_path=candidate.file_path,
                    guideline_uid=None,
                    status="failed",
                    needs_review=False,
                    review_uid=None,
                    retry_counts=retry_counts,
                    error=str(exc),
                )
            )
            return {
                "continue_to_next": True,
                "candidate_index": state["candidate_index"] + 1,
                "summary": summary,
            }

        if not needs_review:
            summary.persisted += 1
            summary.items.append(
                WorkflowItemResult(
                    file_path=candidate.file_path,
                    guideline_uid=persisted.guideline_uid,
                    status="completed",
                    needs_review=False,
                    review_uid=None,
                    retry_counts=retry_counts,
                )
            )
            return {
                "persisted": persisted,
                "needs_review": False,
                "continue_to_next": True,
                "candidate_index": state["candidate_index"] + 1,
                "summary": summary,
            }

        notes = (
            "Low-confidence autonomous decision. "
            f"confidence={scored.confidence_score:.5f}, score={scored.score:.5f}"
        )
        review_uid = self._store.create_guideline_review(
            guideline_id=persisted.guideline_id,
            notes=notes,
        )
        return {
            "persisted": persisted,
            "review_uid": review_uid,
            "needs_review": True,
            "continue_to_next": False,
            "summary": summary,
        }

    def _review_node(self, state: WorkflowGraphState) -> dict:
        summary = state["summary"]
        target = state["target"]
        candidate = state["current_candidate"]
        scored = state["scored"]
        persisted = state["persisted"]
        review_uid = state["review_uid"]
        retry_counts = dict(state["retry_counts"])

        payload = {
            "repository": f"{target.owner}/{target.name}",
            "file_path": candidate.file_path,
            "guideline_uid": persisted.guideline_uid,
            "guideline_id": persisted.guideline_id,
            "review_uid": review_uid,
            "confidence_score": scored.confidence_score,
            "score": scored.score,
        }
        decision = self._resolve_review_decision(payload)
        action = (decision.get("action") or "approved").strip().lower()
        notes = (decision.get("notes") or "").strip() or "Reviewed via HITL."

        if hasattr(self._store, "resolve_guideline_review"):
            self._store.resolve_guideline_review(review_uid=review_uid, action=action, notes=notes)
        if hasattr(self._store, "set_guideline_status"):
            next_status = "active" if action == "approved" else "draft"
            self._store.set_guideline_status(
                guideline_id=persisted.guideline_id,
                status=next_status,
            )

        summary.persisted += 1
        summary.reviews_created += 1
        summary.items.append(
            WorkflowItemResult(
                file_path=candidate.file_path,
                guideline_uid=persisted.guideline_uid,
                status="completed",
                needs_review=True,
                review_uid=review_uid,
                retry_counts=retry_counts,
                error=None,
            )
        )
        return {
            "continue_to_next": True,
            "candidate_index": state["candidate_index"] + 1,
            "summary": summary,
        }

    def _route_after_next_candidate(self, state: WorkflowGraphState) -> str:
        if state.get("continue_to_next") and state.get("current_candidate") is not None:
            return "classify"
        return "end"

    def _route_after_classify(self, state: WorkflowGraphState) -> str:
        return "next" if state.get("continue_to_next") else "score"

    def _route_after_score(self, state: WorkflowGraphState) -> str:
        return "next" if state.get("continue_to_next") else "persist"

    def _route_after_persist(self, state: WorkflowGraphState) -> str:
        if state.get("needs_review"):
            return "review"
        return "next"

    def _resolve_review_decision(self, payload: dict) -> ReviewDecision:
        if self._hitl_resolver is not None:
            return self._hitl_resolver(payload)

        from langgraph.types import interrupt

        response = interrupt(payload)
        if isinstance(response, dict):
            return {
                "action": str(response.get("action", "approved")),
                "notes": str(response.get("notes", "")),
            }
        return {"action": "approved", "notes": ""}

    def _run_with_retries(self, action: Callable, max_retries: int):
        attempts = 0
        while True:
            attempts += 1
            try:
                return action(), attempts
            except TransientStepError:
                if attempts > max_retries:
                    raise


def serialize_graph_summary(summary: WorkflowRunSummary) -> dict:
    """Serialize graph summary to JSON-compatible dict."""
    payload = asdict(summary)
    payload["items"] = [asdict(item) for item in summary.items]
    return payload
