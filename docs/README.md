# Docs

This repo includes a mature Sphinx documentation project with live-reload via Docker.

## Quick start (Docker Compose)

```bash
docker compose up --build
```

- Browse: http://localhost:8000
- Edit sources in `docs/sphinx/src`
  - Architecture pages under `docs/sphinx/src/architecture`

Stop the server:

```bash
docker compose down
```

## Static build (optional)

```bash
docker compose run --rm docs sphinx-build /docs/src /docs/build/html
```

Output is generated in `docs/sphinx/build/html`.
