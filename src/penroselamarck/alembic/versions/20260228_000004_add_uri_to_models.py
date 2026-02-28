"""
Add uri columns to ORM-backed model tables.

Revision ID: 20260228_000004
Revises: 20260227_000003
Create Date: 2026-02-28 00:00:04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260228_000004"
down_revision = "20260227_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exercises", sa.Column("uri", sa.String(length=512), nullable=True))
    op.add_column("practice_sessions", sa.Column("uri", sa.String(length=512), nullable=True))
    op.add_column("attempts", sa.Column("uri", sa.String(length=512), nullable=True))
    op.add_column("performance_summaries", sa.Column("uri", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("performance_summaries", "uri")
    op.drop_column("attempts", "uri")
    op.drop_column("practice_sessions", "uri")
    op.drop_column("exercises", "uri")
