FROM postgres:15-alpine

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ENV POSTGRES_USER=${POSTGRES_USER:-penroselamarck}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-penroselamarckpwd}
ENV POSTGRES_DB=${POSTGRES_DB:-penroselamarck}

## Install build deps and Python + Alembic dependencies
RUN apk add --no-cache python3 py3-pip build-base postgresql-dev

WORKDIR /app

# Copy dependency list first for better layer caching
COPY src/penroselamarck/db/python-requirements.txt ./penroselamarck/db/python-requirements.txt

# Install Python dependencies system-wide (using --break-system-packages due to PEP 668 on Alpine)
RUN python3 -m pip install --upgrade pip --break-system-packages \
 && pip install --no-cache-dir --break-system-packages -r ./penroselamarck/db/python-requirements.txt \
 && rm -rf /root/.cache/pip

# Copy application modules needed for migrations
COPY src/penroselamarck/alembic.ini ./alembic.ini
COPY src/penroselamarck/alembic ./penroselamarck/alembic
COPY src/penroselamarck/core ./penroselamarck/core
COPY src/penroselamarck/db ./penroselamarck/db
COPY src/penroselamarck/models ./penroselamarck/models
COPY src/penroselamarck/schemas ./penroselamarck/schemas
COPY src/penroselamarck/repositories ./penroselamarck/repositories
COPY src/penroselamarck/services ./penroselamarck/services
COPY src/penroselamarck/__init__.py ./penroselamarck/__init__.py

# Set PYTHONPATH so alembic env imports work
ENV PYTHONPATH=/app
RUN mkdir -p /docker-entrypoint-initdb.d /app/bin

COPY src/penroselamarck/db/bin/run_with_migrations.sh /app/bin/run_with_migrations.sh
COPY src/penroselamarck/db/bin/seed.py /app/bin/seed.py
RUN chmod +x /app/bin/run_with_migrations.sh

# Expose the standard Postgres port
EXPOSE 5432

# Use wrapper that invokes original entrypoint then migrations (idempotent)
ENTRYPOINT ["/app/bin/run_with_migrations.sh"]
