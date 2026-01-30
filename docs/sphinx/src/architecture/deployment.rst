Deployment Topology
===================

Containers
----------

- `gateway` (API)
- `ui`
- `orchestrator` (LangGraph runtime)
- `mcp-llm`, `mcp-retrieval`, `mcp-docs`, `mcp-tools`
- `vector-db` (Qdrant)
- `graph-db` (Neo4j)
- `object-store` (MinIO)
- `model-serving` (vLLM/TGI)
- `eval` (RAGAS/TruLens)
- `finetune` (HF Trainer)
- `telemetry` (OTel + Tempo/Jaeger)
- `metrics` (Prometheus + Grafana)
- `logs` (Loki)
- `observability-llm` (Langfuse/Helicone)
- `docs` (Sphinx)

Networking
----------

- All services run on an internal network with a single gateway.
- MCP services are not exposed externally.
- TLS termination at the gateway or ingress controller.
