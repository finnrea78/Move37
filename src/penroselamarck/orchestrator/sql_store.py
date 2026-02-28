"""SQLAlchemy adapter for exercise orchestration tasks."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from penroselamarck.models.exercise import Exercise


class SQLAlchemyWorkflowStore:
    """
    Persistence adapter for exercise-oriented orchestration.

    This store intentionally focuses on exercise class assignment state.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def list_unclassified_exercises(self, limit: int = 100, language: str | None = None) -> list[dict]:
        with Session(self._engine) as session:
            stmt = (
                select(Exercise)
                .where((Exercise.classes.is_(None)) | (Exercise.classes == []))
                .limit(limit)
            )
            if language:
                stmt = stmt.where(Exercise.language == language)
            rows = session.scalars(stmt).all()
            return [
                {
                    "exerciseId": row.id,
                    "question": row.question,
                    "answer": row.answer,
                    "language": row.language,
                    "tags": row.tags or [],
                    "classes": row.classes or [],
                }
                for row in rows
            ]

    def update_exercise_classes(self, exercise_id: str, classes: list[str]) -> bool:
        with Session(self._engine) as session:
            row = session.get(Exercise, exercise_id)
            if row is None:
                return False
            row.classes = classes
            session.add(row)
            session.commit()
            return True
