"""SQLAlchemy models for persisted notes and embedding jobs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class NoteModel(TimestampMixin, Base):
    """User-authored note persisted in the primary database."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_subject: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    source_filename: Mapped[str | None] = mapped_column(String(255))
    linked_activity_id: Mapped[str | None] = mapped_column(String(255), index=True)
    ingest_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    ingest_error: Mapped[str | None] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    last_embedded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    embedding_jobs: Mapped[list["NoteEmbeddingJobModel"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class NoteEmbeddingJobModel(TimestampMixin, Base):
    """Async embedding work item stored in Postgres."""

    __tablename__ = "note_embedding_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    owner_subject: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    job_type: Mapped[str] = mapped_column(String(32), nullable=False, default="upsert")
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    run_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_error: Mapped[str | None] = mapped_column(Text)
    note: Mapped[NoteModel] = relationship(back_populates="embedding_jobs")
