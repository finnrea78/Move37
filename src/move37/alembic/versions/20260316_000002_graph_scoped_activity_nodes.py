"""Scope activity node integrity to each graph.

Revision ID: 20260316_000002
Revises: 20260316_000001
Create Date: 2026-03-16 00:00:02
"""

from __future__ import annotations

from alembic import op


revision = "20260316_000002"
down_revision = "20260316_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("activity_dependencies_parent_id_fkey", "activity_dependencies", type_="foreignkey")
    op.drop_constraint("activity_dependencies_child_id_fkey", "activity_dependencies", type_="foreignkey")
    op.drop_constraint("activity_schedules_earlier_id_fkey", "activity_schedules", type_="foreignkey")
    op.drop_constraint("activity_schedules_later_id_fkey", "activity_schedules", type_="foreignkey")

    op.drop_constraint("activity_nodes_pkey", "activity_nodes", type_="primary")
    op.create_primary_key("pk_activity_nodes", "activity_nodes", ["graph_id", "id"])

    op.create_foreign_key(
        "fk_activity_dependencies_parent_node",
        "activity_dependencies",
        "activity_nodes",
        ["graph_id", "parent_id"],
        ["graph_id", "id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_activity_dependencies_child_node",
        "activity_dependencies",
        "activity_nodes",
        ["graph_id", "child_id"],
        ["graph_id", "id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_activity_schedules_earlier_node",
        "activity_schedules",
        "activity_nodes",
        ["graph_id", "earlier_id"],
        ["graph_id", "id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_activity_schedules_later_node",
        "activity_schedules",
        "activity_nodes",
        ["graph_id", "later_id"],
        ["graph_id", "id"],
        ondelete="CASCADE",
    )

    op.create_check_constraint(
        "ck_activity_dependencies_not_self",
        "activity_dependencies",
        "parent_id <> child_id",
    )
    op.create_check_constraint(
        "ck_activity_schedules_not_self",
        "activity_schedules",
        "earlier_id <> later_id",
    )


def downgrade() -> None:
    op.drop_constraint("ck_activity_schedules_not_self", "activity_schedules", type_="check")
    op.drop_constraint("ck_activity_dependencies_not_self", "activity_dependencies", type_="check")

    op.drop_constraint("fk_activity_schedules_later_node", "activity_schedules", type_="foreignkey")
    op.drop_constraint("fk_activity_schedules_earlier_node", "activity_schedules", type_="foreignkey")
    op.drop_constraint("fk_activity_dependencies_child_node", "activity_dependencies", type_="foreignkey")
    op.drop_constraint("fk_activity_dependencies_parent_node", "activity_dependencies", type_="foreignkey")

    op.drop_constraint("pk_activity_nodes", "activity_nodes", type_="primary")
    op.create_primary_key("activity_nodes_pkey", "activity_nodes", ["id"])

    op.create_foreign_key(
        "activity_dependencies_parent_id_fkey",
        "activity_dependencies",
        "activity_nodes",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "activity_dependencies_child_id_fkey",
        "activity_dependencies",
        "activity_nodes",
        ["child_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "activity_schedules_earlier_id_fkey",
        "activity_schedules",
        "activity_nodes",
        ["earlier_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "activity_schedules_later_id_fkey",
        "activity_schedules",
        "activity_nodes",
        ["later_id"],
        ["id"],
        ondelete="CASCADE",
    )
