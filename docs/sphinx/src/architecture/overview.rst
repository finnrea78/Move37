Overview
========

Penrose-Lamarck currently centers on three product workflows:

- exercise ingestion
- practice sessions
- performance assessment

Those workflows are exposed through two main interfaces:

- REST endpoints under ``/v1/*``
- MCP tools under ``/v1/mcp/sse`` for coding assistants and MCP clients

The repository also includes:

- a read-only web UI that visualizes the exercise graph
- a Postgres-backed persistence layer
- a lightweight orchestrator that classifies exercises and runs graph/search
  refresh tasks
- an observability stack for metrics, traces, and logs

Implementation Shape
--------------------

- FastAPI routers and MCP transport live in ``src/penroselamarck/api``
- business logic lives in ``src/penroselamarck/services``
- SQLAlchemy repositories live in ``src/penroselamarck/repositories``
- ORM models and schemas live in ``src/penroselamarck/models`` and
  ``src/penroselamarck/schemas``
- the web UI lives in ``src/penroselamarck/web``
- orchestration code lives in ``src/penroselamarck/orchestrator``

This is the architecture candidates work against in the hiring exercise.
