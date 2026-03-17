#!/bin/sh
set -e

ORIG_ENTRYPOINT="/usr/local/bin/docker-entrypoint.sh"
if [ ! -x "$ORIG_ENTRYPOINT" ]; then
    echo "[wrapper] Original entrypoint not found at $ORIG_ENTRYPOINT" >&2
    exit 1
fi

DB_ENV_FILE="/app/move37/db/.env"
if [ -f "$DB_ENV_FILE" ]; then
    echo "[wrapper] Loading local DB env from $DB_ENV_FILE"
    set -a
    . "$DB_ENV_FILE"
    set +a
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

if [ "${MOVE37_DB_SEED_MOCK_DATA:-false}" = "true" ]; then
    echo "[wrapper] Seeding local mock data..."
    python3 /app/move37/db/seed_mock_data.py || {
        echo "[wrapper] Mock data seeding failed" >&2
        kill $PG_PID
        exit 1
    }
fi

echo "[wrapper] Migrations complete. Attaching to Postgres foreground..."
wait $PG_PID
