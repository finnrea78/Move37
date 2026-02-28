"""
PerformanceSummary model.

Purpose
--------

Stores denormalized per-exercise aggregates used by selection and reporting.

Example
-------
{
  "performance_summary": {
    "exercise_id": "ex_da_001",
    "uri": "pluid:performance-summary:4f6a92c87d1140d3",
    "total_attempts": 12,
    "pass_rate": 0.83,
    "last_practiced_at": "2026-02-27T10:02:03Z"
  }
}
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from penroselamarck.models.base import Base

if TYPE_CHECKING:
    from penroselamarck.models.exercise import Exercise


class PerformanceSummary(Base):
    """
    PerformanceSummary() -> PerformanceSummary

    ORM model capturing aggregated metrics per exercise.

    Returns
    -------
    PerformanceSummary
        SQLAlchemy-mapped performance summary record.
    """

    __tablename__ = "performance_summaries"

    exercise_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK -> exercises.id (and primary key for one summary per exercise).",
    )
    uri: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Stable external resource URI (pluid:performance-summary:<hash>).",
    )
    total_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total number of attempts observed for this exercise.",
    )
    pass_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Aggregate pass ratio for this exercise.",
    )
    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Timestamp of the latest attempt for this exercise.",
    )

    exercise: Mapped[Exercise] = relationship(back_populates="performance_summary")
