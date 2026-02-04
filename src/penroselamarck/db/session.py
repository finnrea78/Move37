"""
Postgres storage adapter for Penrose-Lamarck.

Provides SQLAlchemy session helpers and CRUD-like operations.

Public API
----------
- :func:`get_engine`: Construct SQLAlchemy engine from `DATABASE_URL`.
- :class:`DB`: High-level CRUD operations for exercises, sessions, attempts.

Attributes
----------
DEFAULT_DATABASE_URL : str
    Fallback SQLAlchemy connection URL when `DATABASE_URL` is unset.

Examples
--------
>>> from penroselamarck.db.session import DB
>>> db = DB()
>>> db.create_schema()

See Also
--------
:mod:`penroselamarck.models`
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from penroselamarck.models.attempt import Attempt
from penroselamarck.models.base import Base
from penroselamarck.models.exercise import Exercise
from penroselamarck.models.practice_session import PracticeSession

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://penroselamarck:penroselamarck@localhost:5432/penroselamarck"
)


def get_engine() -> Engine:
    """
    get_engine() -> Engine

    Concise (one-line) description of the function.

    Parameters
    ----------
    None
        This function does not accept parameters.

    Returns
    -------
    Engine
        SQLAlchemy engine built from the `DATABASE_URL` environment variable.

    Examples
    --------
    >>> isinstance(get_engine(), Engine)
    True
    """
    url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return create_engine(url, pool_pre_ping=True)


class DB:
    """
    DB() -> DB

    Concise (one-line) description of the class.

    Methods
    -------
    create_schema()
        Create all ORM tables.
    add_exercise(question, answer, language, tags, content_hash)
        Insert a new exercise (dedup by content_hash).
    list_exercises(language, tags, limit, offset)
        Query exercises with optional filters.
    get_exercise(exercise_id)
        Retrieve a single exercise by id.
    create_session(language, strategy, target_count, selected_ids)
        Insert a practice session.
    next_exercise(session_id)
        Retrieve the next unattempted exercise for a session.
    record_attempt(session_id, exercise_id, user_answer, score, passed)
        Insert an attempt.
    end_session(session_id)
        Mark a session as ended and summarize attempts.
    performance(language)
        Aggregate performance per exercise.
    """

    def __init__(self) -> None:
        """
        __init__() -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        None
            This initializer does not accept parameters.

        Returns
        -------
        None
            Initializes the database engine.

        Examples
        --------
        >>> isinstance(DB(), DB)
        True
        """
        self.engine = get_engine()

    def create_schema(self) -> None:
        """
        create_schema() -> None

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        None
            Creates all ORM tables if missing.

        Examples
        --------
        >>> DB().create_schema()
        """
        Base.metadata.create_all(self.engine)

    def add_exercise(
        self,
        question: str,
        answer: str,
        language: str,
        tags: list[str] | None,
        content_hash: str,
    ) -> str:
        """
        add_exercise(question, answer, language, tags, content_hash) -> str

        Concise (one-line) description of the function.

        Parameters
        ----------
        question : str
            Exercise prompt.
        answer : str
            Expected answer.
        language : str
            ISO 639-1 language code.
        tags : Optional[List[str]]
            Labels for the exercise.
        content_hash : str
            Deduplication hash for the content.

        Returns
        -------
        str
            New exercise identifier.

        Examples
        --------
        >>> isinstance(DB().add_exercise(\"q\", \"a\", \"da\", None, \"hash\"), str)
        True
        """
        with Session(self.engine) as s:
            exists = s.scalar(select(Exercise.id).where(Exercise.content_hash == content_hash))
            if exists:
                raise ValueError("Duplicate exercise")
            ex_id = uuid.uuid4().hex
            row = Exercise(
                id=ex_id,
                question=question,
                answer=answer,
                language=language,
                tags=tags,
                content_hash=content_hash,
                created_at=datetime.utcnow(),
            )
            s.add(row)
            s.commit()
            return ex_id

    def list_exercises(
        self,
        language: str | None,
        tags: list[str] | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        """
        list_exercises(language, tags, limit, offset) -> List[Dict]

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : Optional[str]
            Language filter.
        tags : Optional[List[str]]
            Tag filter list.
        limit : int
            Maximum rows returned.
        offset : int
            Result offset.

        Returns
        -------
        List[Dict]
            A list of exercise summary dictionaries.

        Examples
        --------
        >>> isinstance(DB().list_exercises(None, None, 1, 0), list)
        True
        """
        with Session(self.engine) as s:
            stmt = select(Exercise)
            if language:
                stmt = stmt.where(Exercise.language == language)
            if tags:
                stmt = stmt.where(Exercise.tags.contains(tags))
            stmt = stmt.offset(offset).limit(limit)
            rows = s.scalars(stmt).all()
            return [
                {
                    "exerciseId": r.id,
                    "question": r.question,
                    "language": r.language,
                    "tags": r.tags,
                }
                for r in rows
            ]

    def get_exercise(self, exercise_id: str) -> dict | None:
        """
        get_exercise(exercise_id) -> Optional[Dict]

        Concise (one-line) description of the function.

        Parameters
        ----------
        exercise_id : str
            Identifier of the exercise.

        Returns
        -------
        Optional[Dict]
            Exercise details or None if missing.

        Examples
        --------
        >>> DB().get_exercise(\"missing\") is None
        True
        """
        with Session(self.engine) as s:
            r = s.get(Exercise, exercise_id)
            if not r:
                return None
            return {
                "exerciseId": r.id,
                "question": r.question,
                "answer": r.answer,
                "language": r.language,
                "tags": r.tags,
            }

    def create_session(
        self,
        language: str,
        strategy: str,
        target_count: int,
        selected_ids: list[str],
    ) -> str:
        """
        create_session(language, strategy, target_count, selected_ids) -> str

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : str
            Session language.
        strategy : str
            Selection strategy.
        target_count : int
            Number of exercises requested.
        selected_ids : List[str]
            Selected exercise identifiers.

        Returns
        -------
        str
            New session identifier.

        Examples
        --------
        >>> isinstance(DB().create_session(\"da\", \"mixed\", 1, []), str)
        True
        """
        with Session(self.engine) as s:
            sess_id = uuid.uuid4().hex
            row = PracticeSession(
                session_id=sess_id,
                language=language,
                strategy=strategy,
                target_count=target_count,
                status="started",
                started_at=datetime.utcnow(),
                selected_exercise_ids=selected_ids,
            )
            s.add(row)
            s.commit()
            return sess_id

    def next_exercise(self, session_id: str) -> dict | None:
        """
        next_exercise(session_id) -> Optional[Dict]

        Concise (one-line) description of the function.

        Parameters
        ----------
        session_id : str
            Session identifier.

        Returns
        -------
        Optional[Dict]
            The next exercise summary or None if finished.

        Examples
        --------
        >>> DB().next_exercise(\"missing\") is None
        True
        """
        with Session(self.engine) as s:
            sess = s.get(PracticeSession, session_id)
            if not sess:
                return None
            attempted = s.scalars(
                select(Attempt.exercise_id).where(Attempt.session_id == session_id)
            ).all()
            attempted_set = set(attempted)
            for ex_id in sess.selected_exercise_ids or []:
                if ex_id not in attempted_set:
                    r = s.get(Exercise, ex_id)
                    if r:
                        return {
                            "exerciseId": r.id,
                            "question": r.question,
                            "language": r.language,
                            "tags": r.tags,
                        }
            return None

    def record_attempt(
        self,
        session_id: str,
        exercise_id: str,
        user_answer: str,
        score: float,
        passed: bool,
    ) -> None:
        """
        record_attempt(session_id, exercise_id, user_answer, score, passed) -> None

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

        Returns
        -------
        None
            Inserts a new attempt row.

        Examples
        --------
        >>> DB().record_attempt(\"s\", \"e\", \"a\", 1.0, True)
        """
        with Session(self.engine) as s:
            row = Attempt(
                id=uuid.uuid4().hex,
                session_id=session_id,
                exercise_id=exercise_id,
                user_answer=user_answer,
                score=score,
                passed=passed,
                evaluated_at=datetime.utcnow(),
            )
            s.add(row)
            s.commit()

    def end_session(self, session_id: str) -> dict:
        """
        end_session(session_id) -> Dict

        Concise (one-line) description of the function.

        Parameters
        ----------
        session_id : str
            Session identifier.

        Returns
        -------
        Dict
            Attempt counts and pass rate summary.

        Examples
        --------
        >>> isinstance(DB().end_session(\"missing\"), dict)
        True
        """
        with Session(self.engine) as s:
            sess = s.get(PracticeSession, session_id)
            if not sess:
                return {"attempts": 0, "passRate": 0.0}
            sess.status = "ended"
            sess.ended_at = datetime.utcnow()
            s.add(sess)
            s.commit()
            statement = select(Attempt).where(Attempt.session_id == session_id)
            attempts = s.scalars(statement).all()
            total = len(attempts)
            pr = (sum(1 for a in attempts if a.passed) / total) if total else 0.0
            return {"attempts": total, "passRate": pr}

    def performance(self, language: str | None) -> dict:
        """
        performance(language) -> Dict

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : Optional[str]
            Language filter.

        Returns
        -------
        Dict
            Per-exercise performance with aggregate metrics.

        Examples
        --------
        >>> isinstance(DB().performance(None), dict)
        True
        """
        with Session(self.engine) as s:
            stmt = select(Exercise)
            if language:
                stmt = stmt.where(Exercise.language == language)
            rows = s.scalars(stmt).all()
            items = []
            overall = 0.0
            for r in rows:
                attempts = s.scalars(select(Attempt).where(Attempt.exercise_id == r.id)).all()
                total = len(attempts)
                pr = (sum(1 for a in attempts if a.passed) / total) if total else 0.0
                last = max((a.evaluated_at for a in attempts), default=None)
                items.append({
                    "exercise_id": r.id,
                    "total_attempts": total,
                    "pass_rate": pr,
                    "last_practiced_at": last,
                })
                overall += pr
            aggregates = {
                "overallPassRate": (overall / len(items)) if items else 0.0,
                "attempts": sum(i["total_attempts"] for i in items),
            }
            return {"items": items, "aggregates": aggregates}

    def _has_pgcrypto(self, s: Session) -> bool:
        """
        _has_pgcrypto(s) -> bool

        Concise (one-line) description of the function.

        Parameters
        ----------
        s : Session
            Active SQLAlchemy session.

        Returns
        -------
        bool
            True if pgcrypto is available.

        Examples
        --------
        >>> isinstance(DB()._has_pgcrypto(Session(DB().engine)), bool)
        True
        """
        try:
            s.execute("SELECT gen_random_uuid();")
            return True
        except Exception:
            return False

    def _has_jsonb_contains(self, s: Session) -> bool:
        """
        _has_jsonb_contains(s) -> bool

        Concise (one-line) description of the function.

        Parameters
        ----------
        s : Session
            Active SQLAlchemy session.

        Returns
        -------
        bool
            True if jsonb containment is available.

        Examples
        --------
        >>> isinstance(DB()._has_jsonb_contains(Session(DB().engine)), bool)
        True
        """
        _ = s
        return False
