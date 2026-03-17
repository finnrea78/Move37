#!/bin/sh
set -e

ORIG_ENTRYPOINT="/usr/local/bin/docker-entrypoint.sh"
if [ ! -x "$ORIG_ENTRYPOINT" ]; then
    echo "[wrapper] Original entrypoint not found at $ORIG_ENTRYPOINT" >&2
    exit 1
fi

"$ORIG_ENTRYPOINT" postgres &
PG_PID=$!

echo "[wrapper] Waiting for Postgres to become available..."
RETRIES=60
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h 127.0.0.1 -p 5432 > /dev/null 2>&1; do
    RETRIES=$((RETRIES - 1))
    if [ "$RETRIES" -le 0 ]; then
        echo "[wrapper] Postgres did not become ready in time" >&2
        exit 1
    fi
    sleep 1
done

export POSTGRES_HOST="127.0.0.1"
export POSTGRES_PORT="5432"
export PYTHONPATH=/app

echo "[wrapper] Postgres is ready, applying migrations..."
alembic -c /app/alembic.ini upgrade head || {
    echo "[wrapper] Migration failed" >&2
    kill $PG_PID
    exit 1
}

echo "[wrapper] Migrations complete. Attaching to Postgres foreground..."
wait $PG_PID
