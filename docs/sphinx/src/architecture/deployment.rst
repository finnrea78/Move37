Deployment Topology
===================

Primary Compose Services
------------------------

The repository is designed around local Docker Compose workflows. The main
services are:

- ``docs`` for live Sphinx preview on port ``8000``
- ``api`` for REST and MCP on port ``8080``
- ``web`` for the exercise graph UI on port ``5173``
- ``db`` for Postgres on port ``5432``
- ``orchestrator`` for exercise post-processing
- ``otel-collector``, ``prometheus``, ``loki``, ``promtail``, and ``grafana``
  for observability
- ``mcp-inspector`` and ``mcp-fastapi`` for MCP inspection and smoke testing

Network Model
-------------

All services join the ``penroselamarck-network`` Docker network.

- Host-side tools should use ``localhost`` for exposed ports.
- Container-to-container traffic uses compose service names such as
  ``penroselamarck-api`` or ``db``.
- The Codex CLI host workflow must use ``http://localhost:8080/v1/mcp/sse``
  rather than the internal API hostname.

Deployment Scope
----------------

These docs focus on the local Docker Compose deployment used for development
and candidate evaluation. The repository also includes infrastructure code
under ``src/penroselamarck/infra/eks``, but that is not the main path for the
exercise.
