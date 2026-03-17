FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends bash git nodejs npm \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY devtools/pyproject.toml ./pyproject.toml
COPY devtools/README.md ./README.md
COPY devtools/src ./src

RUN python -m pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir "setuptools>=69" wheel \
 && pip install --no-cache-dir .

ENTRYPOINT ["mv37-devtools"]
