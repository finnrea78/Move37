# Penrose-Lamarck Orchestrator

This package runs post-create exercise orchestration:

- classify exercises that still have no `classes`
- optionally pre-run semantic search queries
- emit observability metrics/traces via OpenTelemetry

Run:

```bash
python -m penroselamarck.orchestrator
```

## Runtime Environment Variables

- `ORCHESTRATOR_LANGUAGE` (optional): only process/search exercises in one language
- `ORCHESTRATOR_CLASSIFY_LIMIT` (optional, default `100`)
- `ORCHESTRATOR_SEARCH_QUERIES` (optional CSV): queries to run each cycle
- `ORCHESTRATOR_SEARCH_LIMIT` (optional, default `20`)
- `LOG_LEVEL` (optional, default `INFO`)
- `OTEL_ENABLED` (optional, default `true`)
- `OTEL_SERVICE_NAME` (optional, default `penroselamarck-orchestrator`)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (optional, default `http://otel-collector:4318`)
- `OTEL_METRICS_EXPORT_INTERVAL_MS` (optional, default `5000`)

Use `.env.example` as the template for `src/penroselamarck/orchestrator/.env`.
