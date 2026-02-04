"""
Attempt repository.

Handles persistence for graded attempts.

Public API
----------
- :class:`AttemptRepository`: Database operations for attempts.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.db.session import get_engine
>>> repo = AttemptRepository(get_engine())
>>> callable(repo.record_attempt)
True

See Also
--------
:class:`penroselamarck.models.attempt.Attempt`
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from penroselamarck.models.attempt import Attempt


class AttemptRepository:
    """
    AttemptRepository(engine) -> AttemptRepository

    Concise (one-line) description of the repository.

    Methods
    -------
    record_attempt(session_id, exercise_id, user_answer, score, passed)
        Insert an attempt record.
    list_attempts_for_session(session_id)
        Retrieve attempts for a session.
    list_attempts_for_exercise(exercise_id)
        Retrieve attempts for an exercise.
    """

    def __init__(self, engine: Engine) -> None:
        """
        __init__(engine) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine bound to Postgres.

        Returns
        -------
        None
            Initializes the repository.
        """
        self._engine = engine

    def record_attempt(
        self,
        session_id: str,
        exercise_id: str,
        user_answer: str,
        score: float,
        passed: bool,
        evaluated_at: datetime,
    ) -> None:
        """
        record_attempt(session_id, exercise_id, user_answer, score, passed, evaluated_at) -> None

        Concise (one-line) description of the function.

        Parameters
        ----------
        session_id : str
            Session identifier.
        exercise_id : str
            Exercise identifier.
        user_answer : str
            Learner's answer.
        score : float
            Score in [0, 1].
        passed : bool
            Whether the answer passed.
        evaluated_at : datetime
            Timestamp for evaluation.

        Returns
        -------
        None
            Inserts a new attempt row.
        """
        with Session(self._engine) as session:
            row = Attempt(
                id=uuid.uuid4().hex,
                session_id=session_id,
                exercise_id=exercise_id,
                user_answer=user_answer,
                score=score,
                passed=passed,
                evaluated_at=evaluated_at,
            )
            session.add(row)
            session.commit()

    def list_attempts_for_session(self, session_id: str) -> list[Attempt]:
        """
        list_attempts_for_session(session_id) -> List[Attempt]

        Concise (one-line) description of the function.

        Parameters
        ----------
        session_id : str
            Session identifier.

        Returns
        -------
        List[Attempt]
            Attempt records for the session.
        """
        with Session(self._engine) as session:
            stmt = select(Attempt).where(Attempt.session_id == session_id)
            return list(session.scalars(stmt).all())

    def list_attempts_for_exercise(self, exercise_id: str) -> list[Attempt]:
        """
        list_attempts_for_exercise(exercise_id) -> List[Attempt]

        Concise (one-line) description of the function.

        Parameters
        ----------
        exercise_id : str
            Exercise identifier.

        Returns
        -------
        List[Attempt]
            Attempt records for the exercise.
        """
        with Session(self._engine) as session:
            stmt = select(Attempt).where(Attempt.exercise_id == exercise_id)
            return list(session.scalars(stmt).all())
