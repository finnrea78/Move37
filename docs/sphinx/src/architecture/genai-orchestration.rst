Orchestration And MCP
=====================

MCP Surface
-----------

Penrose-Lamarck exposes its assistant-facing functionality through MCP at
``/v1/mcp/sse``. The MCP tool registry maps tool calls onto the same service
layer used by the REST API.

The current tool set includes operations such as:

- authentication and study context
- exercise creation, listing, graph, search, and classification
- bulk import
- practice session start, next, submit, and end
- performance metrics

Current Orchestrator Role
-------------------------

The orchestrator in ``src/penroselamarck/orchestrator`` is currently
exercise-focused rather than a general agent platform. Its runtime behavior is
centered on:

- classifying exercises that do not yet have classes
- optionally running predefined semantic-search queries
- emitting observability metrics and traces

Search And Graph Processing
---------------------------

Graph construction and semantic search currently happen inside
``ExerciseService`` using repository-backed data:

- graph edges are built from shared tags and classes
- semantic search uses normalized token overlap
- class inference uses lightweight heuristics when explicit classes are absent

