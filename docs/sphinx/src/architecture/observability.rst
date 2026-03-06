Observability
=============

Local Stack
-----------

The local observability stack is defined in ``compose.yml`` and includes:

- OpenTelemetry Collector
- Prometheus
- Loki
- Promtail
- Grafana

Data Flow
---------

The current data flow is:

- orchestrator emits OTLP telemetry to the collector
- Prometheus scrapes metrics from the collector
- container logs are tailed by Promtail and shipped to Loki
- Grafana queries Prometheus and Loki

What It Covers Today
--------------------

- orchestrator metrics and traces
- compose-container logs
- dashboards and ad hoc queries through Grafana

The current observability story is strongest around the orchestrator and local
container operations rather than full end-to-end product tracing.
