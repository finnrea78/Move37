"""
Deterministic mock data seeding for Postgres.

Short summary describing the module's purpose.

Public API
----------
- :func:`main`: Entry point that seeds data idempotently.
"""

import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from penroselamarck.models.exercise_orm import ExerciseORM
from penroselamarck.models.practice_session_orm import PracticeSessionORM
from penroselamarck.models.attempt_orm import AttemptORM


def _db_url() -> str:
    """
    _db_url() -> str

    Returns
    -------
    str
        SQLAlchemy connection URL from env vars.
    """
    user = os.getenv("POSTGRES_USER", "penroselamarck")
    password = os.getenv("POSTGRES_PASSWORD", "penroselamarck")
    db = os.getenv("POSTGRES_DB", "penroselamarck")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def _seed_exercises(s: Session) -> List[str]:
    """
    Seed exercises if missing, returning their IDs in order.
    """
    rows = [
        {
            "id": "e0000000000000000000000000000001",
            "question": "hej",
            "answer": "hello",
            "language": "da",
            "tags": ["vocab"],
            "content_hash": "ch_e1",
        },
        {
            "id": "e0000000000000000000000000000002",
            "question": "tak",
            "answer": "thanks",
            "language": "da",
            "tags": ["vocab"],
            "content_hash": "ch_e2",
        },
        {
            "id": "e0000000000000000000000000000003",
            "question": "farvel",
            "answer": "goodbye",
            "language": "da",
            "tags": ["vocab"],
            "content_hash": "ch_e3",
        },
    ]
    ids = []
    for r in rows:
        existing = s.get(ExerciseORM, r["id"]) or s.scalar(
            select(ExerciseORM.id).where(ExerciseORM.content_hash == r["content_hash"]) 
        )
        if not existing:
            s.add(
                ExerciseORM(
                    id=r["id"],
                    question=r["question"],
                    answer=r["answer"],
                    language=r["language"],
                    tags=r["tags"],
                    content_hash=r["content_hash"],
                    created_at=datetime(2024, 1, 1, 0, 0, 0),
                )
            )
        ids.append(r["id"])
    return ids


def _seed_session(s: Session, exercise_ids: List[str]) -> str:
    """
    Seed a practice session with a fixed id and selection.
    """
    sess_id = "s0000000000000000000000000000001"
    existing = s.get(PracticeSessionORM, sess_id)
    if not existing:
        s.add(
            PracticeSessionORM(
                session_id=sess_id,
                language="da",
                strategy="mixed",
                target_count=3,
                status="ended",
                started_at=datetime(2024, 1, 2, 0, 0, 0),
                ended_at=datetime(2024, 1, 2, 0, 30, 0),
                selected_exercise_ids=exercise_ids,
            )
        )
    return sess_id


def _seed_attempts(s: Session, session_id: str, exercise_ids: List[str]) -> None:
    """
    Seed two attempts with deterministic IDs.
    """
    attempts = [
        {
            "id": "a0000000000000000000000000000001",
            "exercise_id": exercise_ids[0],
            "user_answer": "hello",
            "score": 1.0,
            "passed": True,
            "evaluated_at": datetime(2024, 1, 2, 0, 5, 0),
        },
        {
            "id": "a0000000000000000000000000000002",
            "exercise_id": exercise_ids[1],
            "user_answer": "thank you",
            "score": 0.8,
            "passed": True,
            "evaluated_at": datetime(2024, 1, 2, 0, 10, 0),
        },
    ]
    for a in attempts:
        if not s.get(AttemptORM, a["id"]):
            s.add(
                AttemptORM(
                    id=a["id"],
                    session_id=session_id,
                    exercise_id=a["exercise_id"],
                    user_answer=a["user_answer"],
                    score=a["score"],
                    passed=a["passed"],
                    evaluated_at=a["evaluated_at"],
                )
            )


def main() -> None:
    """
    main() -> None

    Seed all tables with deterministic data. Safe to run multiple times.
    """
    engine = create_engine(_db_url(), pool_pre_ping=True)
    with Session(engine) as s:
        ids = _seed_exercises(s)
        sess_id = _seed_session(s, ids)
        _seed_attempts(s, sess_id, ids)
        s.commit()


if __name__ == "__main__":
    main()
