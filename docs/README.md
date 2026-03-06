# Docs

The Sphinx site under `docs/sphinx/src` is the single source of truth for
Penrose-Lamarck documentation.

Published docs: https://genentech.github.io/penrose-lamarck/

## Local preview

```bash
docker compose up --build docs
```

- Browse: http://localhost:8000
- Edit sources in `docs/sphinx/src`

Stop the preview server:

```bash
docker compose down
```

## Static build

```bash
docker compose run --rm docs sphinx-build /docs/src /docs/build/html
```

Generated output is written to `docs/sphinx/build/html`.
