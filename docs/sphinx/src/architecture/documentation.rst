Documentation System
====================

Source Of Truth
---------------

The Sphinx documentation under ``docs/sphinx/src`` is the single source of
truth for project documentation.

- The repository ``README.md`` is intentionally brief and points here.
- Candidate guidance, setup notes, and architecture documentation should live in
  Sphinx rather than being duplicated in the README.

Local Workflow
--------------

Preview the docs locally:

.. code-block:: bash

   docker compose up --build docs

The docs container serves content on ``http://localhost:8000``.

Repository Layout
-----------------

- Source files live under ``docs/sphinx/src``
- Theme and static assets live under ``docs/sphinx/src/_static``
- Sidebar overrides live under ``docs/sphinx/src/_templates``
- Local docs helper notes live in ``docs/README.md``
