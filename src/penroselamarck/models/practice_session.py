"""
PracticeSession model.

Purpose
--------

Stores one learner session configuration, lifecycle state, and selected
exercise queue for a practice run.

Example
-------
{
  "practice_session": {
    "session_id": "sess_20260227_0001",
    "uri": "pluid:practice-session:31d4c6447fabc912",
    "language": "da",
    "strategy": "mixed",
    "target_count": 5,
    "status": "started",
    "started_at": "2026-02-27T10:00:00Z",
    "ended_at": null,
    "selected_exercise_ids": ["ex_da_001", "ex_da_017", "ex_da_021"]
  }
}
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from penroselamarck.models.base import Base

if TYPE_CHECKING:
    from penroselamarck.models.attempt import Attempt


class PracticeSession(Base):
    """
    PracticeSession() -> PracticeSession

    ORM model describing a learner's practice session.

    Returns
    -------
    PracticeSession
        SQLAlchemy-mapped practice session record.
    """

    __tablename__ = "practice_sessions"

    session_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="Stable session identifier (primary key).",
    )
    uri: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Stable external resource URI (pluid:practice-session:<hash>).",
    )
    language: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        comment="Language scope for this practice session.",
    )
    strategy: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Selection strategy key (for example, weakest, spaced, mixed).",
    )
    target_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Requested number of exercises in the session.",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="Session lifecycle status (for example, started or ended).",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Timestamp when session started.",
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Timestamp when session ended.",
    )
    selected_exercise_ids: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Ordered list of selected exercise identifiers.",
    )

    attempts: Mapped[list[Attempt]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
