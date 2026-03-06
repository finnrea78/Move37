Core Components
===============

Clients
-------

- Web UI in ``src/penroselamarck/web``
- REST clients calling ``/v1/*``
- MCP clients (e.g.: Codex CLI) calling ``/v1/mcp/sse``
- Smoke-test tooling under ``tests/mcp``

API Layer
---------

The API layer lives in ``src/penroselamarck/api`` and contains:

- FastAPI server setup
- REST routers for auth, context, exercise, practice, metrics, and train
- MCP transport and tool registry
- dependency wiring for service-container access

Service Layer
-------------

The service layer lives in ``src/penroselamarck/services`` and owns the core
application behavior:

- ``ExerciseService`` for creation, listing, classification, graph building,
  and lightweight semantic search
- ``TrainService`` for batch exercise import
- ``PracticeService`` for session lifecycle and answer evaluation
- ``MetricsService`` for performance aggregation
- ``AuthService`` and ``ContextService`` for user and study-context behavior

Persistence Layer
-----------------

Persistence is backed by Postgres plus SQLAlchemy models and repositories:

- models in ``src/penroselamarck/models``
- repositories in ``src/penroselamarck/repositories``
- migrations in ``src/penroselamarck/alembic``
- runtime DB container in ``src/penroselamarck/db``

Supporting Components
---------------------

- ``src/penroselamarck/orchestrator`` for post-create exercise processing
- ``src/penroselamarck/sdk/ts`` for the TypeScript SDK used by the web UI
- ``src/penroselamarck/otel``, ``prometheus``, ``loki``, ``promtail``, and
  ``grafana`` for observability
