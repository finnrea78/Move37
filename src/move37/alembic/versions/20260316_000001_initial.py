"""
Initial Move37 schema.

Revision ID: 20260316_000001
Revises:
Create Date: 2026-03-16 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260316_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activity_graphs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("owner_subject", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("owner_subject", name="uq_activity_graphs_owner_subject"),
    )

    op.create_table(
        "activity_nodes",
        sa.Column("id", sa.String(length=255), primary_key=True, nullable=False),
        sa.Column("graph_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("best_before", sa.Date(), nullable=True),
        sa.Column("expected_time", sa.Numeric(10, 2), nullable=True),
        sa.Column("real_time", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("expected_effort", sa.Numeric(10, 2), nullable=True),
        sa.Column("real_effort", sa.Numeric(10, 2), nullable=True),
        sa.Column("work_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["graph_id"], ["activity_graphs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_activity_nodes_graph_id", "activity_nodes", ["graph_id"])

    op.create_table(
        "activity_dependencies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("graph_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parent_id", sa.String(length=255), nullable=False),
        sa.Column("child_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["graph_id"], ["activity_graphs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["activity_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["activity_nodes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "graph_id",
            "parent_id",
            "child_id",
            name="uq_activity_dependencies_graph_parent_child",
        ),
    )
    op.create_index("ix_activity_dependencies_graph_id", "activity_dependencies", ["graph_id"])

    op.create_table(
        "activity_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("graph_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("earlier_id", sa.String(length=255), nullable=False),
        sa.Column("later_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["graph_id"], ["activity_graphs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["earlier_id"], ["activity_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["later_id"], ["activity_nodes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "graph_id",
            "earlier_id",
            "later_id",
            name="uq_activity_schedules_graph_earlier_later",
        ),
    )
    op.create_index("ix_activity_schedules_graph_id", "activity_schedules", ["graph_id"])

    op.create_table(
        "github_integrations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False),
        sa.Column("installation_id", sa.String(length=255), nullable=True),
        sa.Column("token_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("login", name="uq_github_integrations_login"),
    )

    op.create_table(
        "calendar_connections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_calendar_id", sa.String(length=255), nullable=False),
        sa.Column("owner_email", sa.String(length=255), nullable=True),
        sa.Column("sync_token", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "provider",
            "external_calendar_id",
            name="uq_calendar_connections_provider_calendar",
        ),
    )

    op.create_table(
        "bank_account_connections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_account_id", sa.String(length=255), nullable=False),
        sa.Column("iban", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=12), nullable=True),
        sa.Column("token_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "provider",
            "external_account_id",
            name="uq_bank_account_connections_provider_account",
        ),
    )


def downgrade() -> None:
    op.drop_table("bank_account_connections")
    op.drop_table("calendar_connections")
    op.drop_table("github_integrations")
    op.drop_index("ix_activity_schedules_graph_id", table_name="activity_schedules")
    op.drop_table("activity_schedules")
    op.drop_index("ix_activity_dependencies_graph_id", table_name="activity_dependencies")
    op.drop_table("activity_dependencies")
    op.drop_index("ix_activity_nodes_graph_id", table_name="activity_nodes")
    op.drop_table("activity_nodes")
    op.drop_table("activity_graphs")
