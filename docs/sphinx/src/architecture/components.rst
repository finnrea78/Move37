Core Components
===============

Domain Layer
------------

- **Entities:** Learner profile, learning unit, reasoning trace, mastery state.
- **Value objects:** Concept, skill level, evidence, learning objective.
- **Use-cases:** Ingestion, study plan generation, Socratic tutoring, mastery
  assessment, profile evolution.

Application Layer
-----------------

- **Service orchestration:** Interactors coordinate workflows.
- **Policy enforcement:** Evaluation, safety, and governance gates.
- **State management:** Immutable state transitions and audit trails.

Ports (Interfaces)
------------------

- `LLMPort`
- `RetrieverPort`
- `VectorStorePort`
- `GraphStorePort`
- `DocStorePort`
- `EvalPort`
- `FineTunePort`
- `TelemetryPort`

Infrastructure Adapters
-----------------------

- **LLM serving:** vLLM or TGI.
- **Vector DB:** Qdrant or Weaviate.
- **Graph DB:** Neo4j for concept relationships.
- **Object storage:** MinIO for raw documents.
- **Observability:** OpenTelemetry, Grafana, Tempo/Jaeger, Loki.
