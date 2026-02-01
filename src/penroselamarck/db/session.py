    """
Postgres storage adapter for Penrose-Lamarck.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :func:`get_engine`: Construct SQLAlchemy engine from `DATABASE_URL`.
- :class:`DB`: High-level CRUD operations for exercises, sessions, attempts.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.storage.postgres import DB
>>> db = DB()
>>> db.create_schema()

See Also
--------
:mod:`penroselamarck.mcp.server`
"""

import os
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import (
    create_engine,
    select,
    func,
)
from sqlalchemy.orm import Session

from penroselamarck.models.base import Base
from penroselamarck.models.exercise_orm import ExerciseORM
from penroselamarck.models.practice_session_orm import PracticeSessionORM
from penroselamarck.models.attempt_orm import AttemptORM


def get_engine():
    """
    get_engine() -> Engine

    Concise (one-line) description of the function.

    Returns
    -------
    Engine
        SQLAlchemy engine built from the `DATABASE_URL` environment variable.
    """
    url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/penrose")
    return create_engine(url, pool_pre_ping=True)




class DB:
    """
    DB() -> DB

    Concise (one-line) description of the class.

    Extended description of the class, if necessary.

    Methods
    -------
    create_schema()
        Create all ORM tables.
    add_exercise(question, answer, language, tags)
        Insert a new exercise (dedup by content_hash).
    list_exercises(language, tags, limit, offset)
        Query exercises with optional filters.
    create_session(language, strategy, target_count, selected_ids)
        Insert a practice session.
    next_exercise(session_id)
        Retrieve the next unattempted exercise for a session.
    record_attempt(session_id, exercise_id, user_answer, score, passed)
        Insert an attempt.
    session_summary(session_id)
        Compute attempts count and pass rate.
    performance(language)
        Aggregate performance per exercise.

    Examples
    --------
    >>> db = DB(); db.create_schema()
    >>> ids = [ex["exerciseId"] for ex in db.list_exercises("da", None, 100, 0)]
    """

    def __init__(self):
        self.engine = get_engine()

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def add_exercise(self, question: str, answer: str, language: str, tags: Optional[List[str]], content_hash: str) -> str:
        with Session(self.engine) as s:
            exists = s.scalar(select(ExerciseORM.id).where(ExerciseORM.content_hash == content_hash))
            if exists:
                raise ValueError("Duplicate exercise")
            ex_id = func.replace(func.gen_random_uuid().cast(String), '-', '') if self._has_pgcrypto(s) else None
            if not ex_id:
                # fallback uuid generation
                import uuid as _uuid
                ex_id = str(_uuid.uuid4())
            row = ExerciseORM(id=ex_id, question=question, answer=answer, language=language, tags=tags, content_hash=content_hash)
            s.add(row)
            s.commit()
            return ex_id

    def list_exercises(self, language: Optional[str], tags: Optional[List[str]], limit: int, offset: int) -> List[Dict]:
        with Session(self.engine) as s:
            stmt = select(ExerciseORM)
            if language:
                stmt = stmt.where(ExerciseORM.language == language)
            # simple tags containment
            if tags:
                stmt = stmt.where(func.jsonb_contains(ExerciseORM.tags, tags)) if self._has_jsonb_contains(s) else stmt
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

    def get_exercise(self, exercise_id: str) -> Optional[Dict]:
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
            A dictionary with question, answer, language, tags, or None if missing.
        """
        with Session(self.engine) as s:
            r = s.get(ExerciseORM, exercise_id)
            if not r:
                return None
            return {
                "exerciseId": r.id,
                "question": r.question,
                "answer": r.answer,
                "language": r.language,
                "tags": r.tags,
            }

    def create_session(self, language: str, strategy: str, target_count: int, selected_ids: List[str]) -> str:
        with Session(self.engine) as s:
            import uuid as _uuid
            sess_id = str(_uuid.uuid4())
            row = PracticeSessionORM(
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

    def next_exercise(self, session_id: str) -> Optional[Dict]:
        with Session(self.engine) as s:
            sess = s.get(PracticeSessionORM, session_id)
            if not sess:
                return None
            attempted = s.scalars(select(AttemptORM.exercise_id).where(AttemptORM.session_id == session_id)).all()
            attempted_set = set(attempted)
            for ex_id in (sess.selected_exercise_ids or []):
                if ex_id not in attempted_set:
                    r = s.get(ExerciseORM, ex_id)
                    if r:
                        return {"exerciseId": r.id, "question": r.question, "language": r.language, "tags": r.tags}
            return None

    def record_attempt(self, session_id: str, exercise_id: str, user_answer: str, score: float, passed: bool) -> None:
        with Session(self.engine) as s:
            import uuid as _uuid
            row = AttemptORM(
                id=str(_uuid.uuid4()),
                session_id=session_id,
                exercise_id=exercise_id,
                user_answer=user_answer,
                score=score,
                passed=passed,
                evaluated_at=datetime.utcnow(),
            )
            s.add(row)
            s.commit()

    def end_session(self, session_id: str) -> Dict:
        with Session(self.engine) as s:
            sess = s.get(PracticeSessionORM, session_id)
            if not sess:
                return {"attempts": 0, "passRate": 0.0}
            sess.status = "ended"
            sess.ended_at = datetime.utcnow()
            s.add(sess)
            s.commit()
            attempts = s.scalars(select(AttemptORM).where(AttemptORM.session_id == session_id)).all()
            total = len(attempts)
            pr = (sum(1 for a in attempts if a.passed) / total) if total else 0.0
            return {"attempts": total, "passRate": pr}

    def performance(self, language: Optional[str]) -> Dict:
        with Session(self.engine) as s:
            stmt = select(ExerciseORM)
            if language:
                stmt = stmt.where(ExerciseORM.language == language)
            rows = s.scalars(stmt).all()
            items = []
            overall = 0.0
            for r in rows:
                attempts = s.scalars(select(AttemptORM).where(AttemptORM.exercise_id == r.id)).all()
                total = len(attempts)
                pr = (sum(1 for a in attempts if a.passed) / total) if total else 0.0
                last = max((a.evaluated_at for a in attempts), default=None)
                items.append({"exercise_id": r.id, "total_attempts": total, "pass_rate": pr, "last_practiced_at": last})
                overall += pr
            aggregates = {"overallPassRate": (overall / len(items)) if items else 0.0, "attempts": sum(i["total_attempts"] for i in items)}
            return {"items": items, "aggregates": aggregates}

    def _has_pgcrypto(self, s: Session) -> bool:
        try:
            s.execute("SELECT gen_random_uuid();")
            return True
        except Exception:
            return False

    def _has_jsonb_contains(self, s: Session) -> bool:
        # Placeholder feature detection; always false for now
        return False
