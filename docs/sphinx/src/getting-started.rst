Getting Started
===============

This page covers the local workflows that are used most often when working on
Penrose-Lamarck.

Quick Start
-----------

Preview the documentation locally:

.. code-block:: bash

   docker compose up --build docs

Open ``http://localhost:8000``.

Run the API and database locally:

.. code-block:: bash

   docker compose up -d --build db api

Health check:

.. code-block:: bash

   curl -s http://localhost:8080/health

Run the web UI:

.. code-block:: bash

   docker compose up -d --build web

Open ``http://localhost:5173``.

Run the exercise orchestrator with observability:

.. code-block:: bash

   docker compose up -d db otel-collector prometheus loki promtail grafana orchestrator

Codex CLI And MCP
-----------------

Codex CLI MCP testing must be done from the host machine, not from inside the
devcontainer.

- Use ``penroselamarck-local`` at ``http://localhost:8080/v1/mcp/sse``.
- Do not use ``penroselamarck-api`` from host-side Codex CLI. That hostname is
  only reachable inside the Docker network or devcontainer.

Local No-Auth Mode
------------------

For local development, set ``AUTH_DISABLED=true`` in
``src/penroselamarck/api/.env`` and run ``db`` plus ``api``.

In this mode:

- Codex may show ``Auth: Unsupported`` for ``penroselamarck-local``.
- OAuth discovery probes may still be attempted by MCP clients and can return
  ``404``.
- Those ``404`` responses are expected and do not indicate an API failure.

If you still see a stale ``penroselamarck-devcontainer`` MCP entry with
``Tools: (none)``, remove it and continue using ``penroselamarck-local``.

Optional Deterministic Mock Data
--------------------------------

The Postgres container can seed deterministic mock data at startup.

- Configure ``src/penroselamarck/db/.env``.
- Set ``DB_MOCK_DATA=true`` to run the seed module after migrations.
- Leave ``DB_MOCK_DATA=false`` to skip mock seeding.

Example:

.. code-block:: bash

   docker compose up -d --build db api web

TypeScript SDK
--------------

Penrose-Lamarck publishes a TypeScript SDK package:

- Package name: ``@genentech/penroselamarck``
- Source path: ``src/penroselamarck/sdk/ts``
- Registry: ``npm.pkg.github.com``

The local Docker workflow uses the SDK from the repository source tree.
