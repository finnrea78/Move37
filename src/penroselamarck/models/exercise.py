"""
Exercise model.

Purpose
--------

Stores the canonical exercise bank (question, answer, language, and metadata)
used by practice sessions and performance aggregation.

Example
-------
{
  "exercise": {
    "id": "ex_da_001",
    "uri": "pluid:exercise:6ee4c2db8c24e4d9",
    "question": "Translate to Danish: \\"hello\\"",
    "answer": "hej",
    "language": "da",
    "tags": ["greetings", "vocabulary"],
    "classes": ["beginner", "core-lexicon"],
    "content_hash": "9b4d6f95d5c3f5c7f6c2a11f86a88f4f86f9d4a2f730f6b73d0be02c1ee11e0d",
    "created_at": "2026-02-27T09:30:00Z"
  }
}
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from penroselamarck.models.base import Base

if TYPE_CHECKING:
    from penroselamarck.models.attempt import Attempt
    from penroselamarck.models.performance_summary import PerformanceSummary


class Exercise(Base):
    """
    Exercise() -> Exercise

    ORM model for a learning exercise.

    Returns
    -------
    Exercise
        SQLAlchemy-mapped exercise record.
    """

    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="Stable exercise identifier (primary key).",
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Prompt text shown to learners.",
    )
    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Canonical expected answer used for evaluation.",
    )
    uri: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Stable external resource URI (pluid:exercise:<hash>).",
    )
    language: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        index=True,
        comment="Language code used for filtering and session matching.",
    )
    tags: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Optional tags used for retrieval and reporting.",
    )
    classes: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Optional curriculum classes or group labels.",
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="Deduplication hash of normalized exercise content.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Exercise creation timestamp.",
    )

    attempts: Mapped[list[Attempt]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    performance_summary: Mapped[PerformanceSummary | None] = relationship(
        back_populates="exercise",
        uselist=False,
        cascade="all, delete-orphan",
    )
