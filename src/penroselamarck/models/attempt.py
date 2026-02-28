"""
Attempt model.

Purpose
--------

Stores one evaluated learner answer for one exercise within one session.

Example
-------
{
  "attempt": {
    "id": "att_20260227_00042",
    "uri": "pluid:attempt:f2ea71ad10b9cd5e",
    "session_id": "sess_20260227_0001",
    "exercise_id": "ex_da_001",
    "user_answer": "hej",
    "score": 1.0,
    "passed": true,
    "evaluated_at": "2026-02-27T10:02:03Z"
  }
}
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from penroselamarck.models.base import Base

if TYPE_CHECKING:
    from penroselamarck.models.exercise import Exercise
    from penroselamarck.models.practice_session import PracticeSession


class Attempt(Base):
    """
    Attempt() -> Attempt

    ORM model representing a graded attempt for a specific exercise.

    Returns
    -------
    Attempt
        SQLAlchemy-mapped attempt record.
    """

    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="Stable attempt identifier (primary key).",
    )
    uri: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Stable external resource URI (pluid:attempt:<hash>).",
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("practice_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK -> practice_sessions.session_id containing this attempt.",
    )
    exercise_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK -> exercises.id answered by this attempt.",
    )
    user_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Learner submitted answer text.",
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Numeric evaluation score in the [0,1] range.",
    )
    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Whether attempt met the pass threshold.",
    )
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Timestamp when attempt was evaluated.",
    )

    session: Mapped[PracticeSession] = relationship(back_populates="attempts")
    exercise: Mapped[Exercise] = relationship(back_populates="attempts")
