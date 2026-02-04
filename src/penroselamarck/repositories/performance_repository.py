"""
Performance repository.

Aggregates attempt data into per-exercise performance summaries.

Public API
----------
- :class:`PerformanceRepository`: Performance aggregation operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.db.session import get_engine
>>> repo = PerformanceRepository(get_engine())
>>> callable(repo.performance)
True

See Also
--------
:class:`penroselamarck.models.performance_summary.PerformanceSummary`
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from penroselamarck.models.attempt import Attempt
from penroselamarck.models.exercise import Exercise


class PerformanceRepository:
    """
    PerformanceRepository(engine) -> PerformanceRepository

    Concise (one-line) description of the repository.

    Methods
    -------
    performance(language)
        Aggregate per-exercise performance stats.
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
        """
        with Session(self._engine) as session:
            stmt = select(Exercise)
            if language:
                stmt = stmt.where(Exercise.language == language)
            rows = session.scalars(stmt).all()
            items = []
            overall = 0.0
            for row in rows:
                attempts = session.scalars(
                    select(Attempt).where(Attempt.exercise_id == row.id)
                ).all()
                total = len(attempts)
                pass_rate = (sum(1 for a in attempts if a.passed) / total) if total else 0.0
                last = max((a.evaluated_at for a in attempts), default=None)
                items.append({
                    "exercise_id": row.id,
                    "total_attempts": total,
                    "pass_rate": pass_rate,
                    "last_practiced_at": last,
                })
                overall += pass_rate
            aggregates = {
                "overallPassRate": (overall / len(items)) if items else 0.0,
                "attempts": sum(i["total_attempts"] for i in items),
            }
            return {"items": items, "aggregates": aggregates}
