"""Seed local mock data after migrations when requested."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from move37.default_graph import build_default_graph
from move37.repositories.activity_graph import ActivityGraphRepository


def build_database_url() -> str:
    configured = os.environ.get("MOVE37_DATABASE_URL")
    if configured:
        return configured

    user = os.environ.get("POSTGRES_USER", "move37")
    password = os.environ.get("POSTGRES_PASSWORD", "move37")
    db = os.environ.get("POSTGRES_DB", "move37")
    host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    port = os.environ.get("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def seed_mock_data(subject: str, database_url: str | None = None) -> bool:
    engine = create_engine(database_url or build_database_url(), future=True)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    try:
        with session_factory() as session:
            repository = ActivityGraphRepository(session)
            if repository.get_snapshot(subject) is not None:
                return False
            repository.save_snapshot(subject, build_default_graph())
            session.commit()
            return True
    finally:
        engine.dispose()


def main() -> int:
    subject = os.environ.get("MOVE37_DB_SEED_SUBJECT") or os.environ.get("MOVE37_API_BEARER_SUBJECT") or "local-user"
    seeded = seed_mock_data(subject)
    status = "seeded" if seeded else "already present"
    print(f"[seed] Mock graph for subject '{subject}': {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
