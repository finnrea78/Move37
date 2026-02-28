"""OpenTelemetry wiring and runtime metrics for the orchestrator."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from opentelemetry import metrics, trace

if TYPE_CHECKING:
    from penroselamarck.orchestrator.models import WorkflowRunSummary

_LOGGER = logging.getLogger(__name__)
_TRACER_NAME = "penroselamarck.orchestrator"
_METER_NAME = "penroselamarck.orchestrator"


@dataclass(frozen=True)
class _OTelSettings:
    enabled: bool
    endpoint: str
    service_name: str
    metrics_export_interval_ms: int

    @classmethod
    def from_env(cls) -> _OTelSettings:
        enabled = _bool_env("OTEL_ENABLED", default=True)
        endpoint = (
            os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
            or "http://otel-collector:4318"
        )
        service_name = os.environ.get("OTEL_SERVICE_NAME", "").strip() or "penroselamarck-orchestrator"
        interval_raw = os.environ.get("OTEL_METRICS_EXPORT_INTERVAL_MS", "").strip() or "5000"
        return cls(
            enabled=enabled,
            endpoint=endpoint.rstrip("/"),
            service_name=service_name,
            metrics_export_interval_ms=int(interval_raw),
        )

    @property
    def metrics_endpoint(self) -> str:
        return _otlp_signal_endpoint(self.endpoint, "metrics")

    @property
    def traces_endpoint(self) -> str:
        return _otlp_signal_endpoint(self.endpoint, "traces")


class OrchestratorTelemetry:
    """Metrics and trace helpers for orchestration workflow execution."""

    def __init__(self) -> None:
        tracer = trace.get_tracer(_TRACER_NAME)
        meter = metrics.get_meter(_METER_NAME)
        self._tracer = tracer
        self._targets_total = meter.create_counter(
            "penroselamarck.orchestrator.targets.total",
            description="Number of repositories resolved for orchestration.",
            unit="1",
        )
        self._runs_total = meter.create_counter(
            "penroselamarck.orchestrator.runs.total",
            description="Number of repository runs attempted.",
            unit="1",
        )
        self._errors_total = meter.create_counter(
            "penroselamarck.orchestrator.errors.total",
            description="Number of repository-level orchestration errors.",
            unit="1",
        )
        self._interrupts_total = meter.create_counter(
            "penroselamarck.orchestrator.hitl_interrupts.total",
            description="Number of HITL interrupts emitted by workflow execution.",
            unit="1",
        )
        self._processed_total = meter.create_counter(
            "penroselamarck.orchestrator.exercises.processed.total",
            description="Number of exercises processed by orchestrator runs.",
            unit="1",
        )
        self._persisted_total = meter.create_counter(
            "penroselamarck.orchestrator.exercises.persisted.total",
            description="Number of exercises updated by orchestrator runs.",
            unit="1",
        )
        self._reviews_total = meter.create_counter(
            "penroselamarck.orchestrator.exercises.reviews.total",
            description="Reserved counter for review actions triggered by orchestrator runs.",
            unit="1",
        )
        self._failed_total = meter.create_counter(
            "penroselamarck.orchestrator.exercises.failed.total",
            description="Number of exercise items that failed processing.",
            unit="1",
        )
        self._duration_seconds = meter.create_histogram(
            "penroselamarck.orchestrator.repository.duration.seconds",
            description="End-to-end workflow duration per repository.",
            unit="s",
        )

    @contextmanager
    def repository_span(self, repository: str) -> Iterator[None]:
        with self._tracer.start_as_current_span(
            "orchestrator.repository.run",
            attributes={"penroselamarck.repository": repository},
        ):
            yield

    def record_targets_resolved(self, count: int) -> None:
        self._targets_total.add(max(count, 0))

    def record_repository_run_started(self, repository: str) -> None:
        self._runs_total.add(1, {"penroselamarck.repository": repository})

    def record_hitl_interrupt(self, repository: str) -> None:
        self._interrupts_total.add(1, {"penroselamarck.repository": repository})

    def record_repository_error(self, repository: str, error_type: str) -> None:
        self._errors_total.add(
            1,
            {"penroselamarck.repository": repository, "penroselamarck.error_type": error_type},
        )

    def record_summary(self, summary: WorkflowRunSummary, duration_seconds: float) -> None:
        attributes = {"penroselamarck.repository": summary.repository}
        self._processed_total.add(summary.processed, attributes)
        self._persisted_total.add(summary.persisted, attributes)
        self._reviews_total.add(summary.reviews_created, attributes)
        self._failed_total.add(summary.failed, attributes)
        self._duration_seconds.record(max(duration_seconds, 0.0), attributes)


def configure_observability() -> OrchestratorTelemetry:
    """Configure OTel providers from env and return telemetry helpers."""
    settings = _OTelSettings.from_env()
    telemetry = OrchestratorTelemetry()
    if not settings.enabled:
        _LOGGER.info("orchestrator telemetry disabled by OTEL_ENABLED")
        return telemetry

    try:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.service_name})
        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.traces_endpoint))
        )
        trace.set_tracer_provider(trace_provider)

        metric_reader = PeriodicExportingMetricReader(
            exporter=OTLPMetricExporter(endpoint=settings.metrics_endpoint),
            export_interval_millis=settings.metrics_export_interval_ms,
        )
        metric_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
        metrics.set_meter_provider(metric_provider)
        _LOGGER.info(
            "orchestrator telemetry configured service=%s endpoint=%s",
            settings.service_name,
            settings.endpoint,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime fallback
        _LOGGER.warning("failed to initialize orchestrator telemetry: %s", exc)

    return OrchestratorTelemetry()


def _otlp_signal_endpoint(base_endpoint: str, signal: str) -> str:
    if f"/v1/{signal}" in base_endpoint:
        return base_endpoint
    if base_endpoint.endswith("/v1"):
        return f"{base_endpoint}/{signal}"
    return f"{base_endpoint}/v1/{signal}"


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}
