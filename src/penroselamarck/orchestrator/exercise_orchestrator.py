"""Exercise-focused orchestration runtime."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from penroselamarck.orchestrator.models import WorkflowRunSummary
from penroselamarck.orchestrator.observability import OrchestratorTelemetry
from penroselamarck.services.container import ServiceContainer


@dataclass(frozen=True)
class ExerciseOrchestratorSettings:
    """Runtime settings for the exercise orchestrator."""

    language: str | None
    classify_limit: int
    search_queries: list[str]
    search_limit: int

    @classmethod
    def from_env(cls) -> ExerciseOrchestratorSettings:
        language = os.environ.get("ORCHESTRATOR_LANGUAGE", "").strip() or None
        classify_limit = int(
            os.environ.get("ORCHESTRATOR_CLASSIFY_LIMIT", "").strip() or "100"
        )
        search_limit = int(os.environ.get("ORCHESTRATOR_SEARCH_LIMIT", "").strip() or "20")
        search_queries = _split_csv(os.environ.get("ORCHESTRATOR_SEARCH_QUERIES", ""))
        return cls(
            language=language,
            classify_limit=max(classify_limit, 1),
            search_queries=search_queries,
            search_limit=max(search_limit, 1),
        )


class ExerciseOrchestrator:
    """Coordinates post-create exercise classification and search tasks."""

    def __init__(self, services: ServiceContainer, telemetry: OrchestratorTelemetry) -> None:
        self._services = services
        self._telemetry = telemetry

    def run_once(self, settings: ExerciseOrchestratorSettings) -> dict:
        """Execute one orchestration cycle and return run details."""
        repository = "penrose-lamarck/exercises"
        started_at = time.perf_counter()
        summary = WorkflowRunSummary(repository=repository)

        self._services.schema_service.create_schema()
        self._telemetry.record_targets_resolved(1)
        self._telemetry.record_repository_run_started(repository)

        with self._telemetry.repository_span(repository):
            classify_result = self._services.exercise_service.classify_unclassified_exercises(
                limit=settings.classify_limit
            )
            summary.processed = int(classify_result.get("scanned", 0))
            summary.persisted = int(classify_result.get("updated", 0))

            graph = self._services.exercise_service.build_exercise_graph(
                language=settings.language
            )
            query_results: list[dict] = []
            for query in settings.search_queries:
                hits = self._services.exercise_service.semantic_search_exercises(
                    query=query,
                    language=settings.language,
                    limit=settings.search_limit,
                )
                query_results.append(
                    {
                        "query": query,
                        "hits": hits,
                        "total": len(hits),
                    }
                )

        self._telemetry.record_summary(
            summary=summary,
            duration_seconds=time.perf_counter() - started_at,
        )

        return {
            "classification": classify_result,
            "graph": {
                "nodes": len(graph.get("nodes", [])),
                "edges": len(graph.get("edges", [])),
            },
            "search": query_results,
        }


def _split_csv(raw: str) -> list[str]:
    return [item for item in (chunk.strip() for chunk in raw.split(",")) if item]
