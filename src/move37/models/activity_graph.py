"""SQLAlchemy models for persisted activity graphs."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class ActivityGraphModel(TimestampMixin, Base):
    """Owner-scoped activity graph root record."""

    __tablename__ = "activity_graphs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_subject: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    nodes: Mapped[list["ActivityNodeModel"]] = relationship(
        back_populates="graph",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    dependencies: Mapped[list["ActivityDependencyModel"]] = relationship(
        back_populates="graph",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    schedules: Mapped[list["ActivityScheduleModel"]] = relationship(
        back_populates="graph",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ActivityNodeModel(TimestampMixin, Base):
    """Persisted activity node."""

    __tablename__ = "activity_nodes"
    __table_args__ = (
        PrimaryKeyConstraint("graph_id", "id", name="pk_activity_nodes"),
    )

    graph_id: Mapped[int] = mapped_column(
        ForeignKey("activity_graphs.id", ondelete="CASCADE"),
        nullable=False,
    )
    id: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(String, nullable=False, default="")
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="activity")
    linked_note_id: Mapped[int | None] = mapped_column(Integer, index=True)
    start_date: Mapped[date | None] = mapped_column(Date)
    best_before: Mapped[date | None] = mapped_column(Date)
    expected_time: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))
    real_time: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), default=0, nullable=False)
    expected_effort: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))
    real_effort: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))
    work_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    graph: Mapped[ActivityGraphModel] = relationship(back_populates="nodes")


class ActivityDependencyModel(Base):
    """Persisted dependency edge between nodes."""

    __tablename__ = "activity_dependencies"
    __table_args__ = (
        CheckConstraint("parent_id <> child_id", name="ck_activity_dependencies_not_self"),
        ForeignKeyConstraint(
            ["graph_id", "parent_id"],
            ["activity_nodes.graph_id", "activity_nodes.id"],
            ondelete="CASCADE",
            name="fk_activity_dependencies_parent_node",
        ),
        ForeignKeyConstraint(
            ["graph_id", "child_id"],
            ["activity_nodes.graph_id", "activity_nodes.id"],
            ondelete="CASCADE",
            name="fk_activity_dependencies_child_node",
        ),
        UniqueConstraint("graph_id", "parent_id", "child_id", name="uq_activity_dependencies_graph_parent_child"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    graph_id: Mapped[int] = mapped_column(
        ForeignKey("activity_graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    child_id: Mapped[str] = mapped_column(String(255), nullable=False)
    graph: Mapped[ActivityGraphModel] = relationship(back_populates="dependencies")


class ActivityScheduleModel(Base):
    """Persisted ordering edge between peer nodes."""

    __tablename__ = "activity_schedules"
    __table_args__ = (
        CheckConstraint("earlier_id <> later_id", name="ck_activity_schedules_not_self"),
        ForeignKeyConstraint(
            ["graph_id", "earlier_id"],
            ["activity_nodes.graph_id", "activity_nodes.id"],
            ondelete="CASCADE",
            name="fk_activity_schedules_earlier_node",
        ),
        ForeignKeyConstraint(
            ["graph_id", "later_id"],
            ["activity_nodes.graph_id", "activity_nodes.id"],
            ondelete="CASCADE",
            name="fk_activity_schedules_later_node",
        ),
        UniqueConstraint("graph_id", "earlier_id", "later_id", name="uq_activity_schedules_graph_earlier_later"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    graph_id: Mapped[int] = mapped_column(
        ForeignKey("activity_graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    earlier_id: Mapped[str] = mapped_column(String(255), nullable=False)
    later_id: Mapped[str] = mapped_column(String(255), nullable=False)
    graph: Mapped[ActivityGraphModel] = relationship(back_populates="schedules")
