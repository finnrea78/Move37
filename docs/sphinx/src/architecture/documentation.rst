Documentation System
====================

Sphinx Container
----------------

- Sphinx runs in its own container.
- Source lives under `docs/sphinx/src`.
- Build output is served by a lightweight web server.

Expected Workflow
-----------------

1. Edit reStructuredText sources.
2. Build docs in the Sphinx container.
3. Serve static output via the docs container.
