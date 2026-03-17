FROM postgres:16-alpine

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ENV POSTGRES_USER=${POSTGRES_USER:-move37}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-move37}
ENV POSTGRES_DB=${POSTGRES_DB:-move37}

RUN apk add --no-cache python3 py3-pip build-base postgresql-dev

WORKDIR /app

COPY src/move37/db/python-requirements.txt ./move37/db/python-requirements.txt
RUN python3 -m pip install --upgrade pip --break-system-packages \
 && pip install --no-cache-dir --break-system-packages -r ./move37/db/python-requirements.txt \
 && rm -rf /root/.cache/pip

COPY src/move37/alembic.ini ./alembic.ini
COPY src/move37/alembic ./move37/alembic
COPY src/move37/models ./move37/models
COPY src/move37/repositories ./move37/repositories
COPY src/move37/schemas ./move37/schemas
COPY src/move37/services ./move37/services
COPY src/move37/default_graph.py ./move37/default_graph.py
COPY src/move37/bank_account.py ./move37/bank_account.py
COPY src/move37/calendar.py ./move37/calendar.py
COPY src/move37/github.py ./move37/github.py
COPY src/move37/__init__.py ./move37/__init__.py
ENV PYTHONPATH=/app

RUN mkdir -p /docker-entrypoint-initdb.d /app/bin
COPY src/move37/db/initdb.d/ /docker-entrypoint-initdb.d/
COPY src/move37/db/bin/run_with_migrations.sh /app/bin/run_with_migrations.sh
RUN chmod +x /app/bin/run_with_migrations.sh

EXPOSE 5432

ENTRYPOINT ["/app/bin/run_with_migrations.sh"]
