"""
Add exercise classes JSON column.

Revision ID: 20260227_000003
Revises: 20260203_000002
Create Date: 2026-02-27 00:00:03
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260227_000003"
down_revision = "20260203_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exercises", sa.Column("classes", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("exercises", "classes")
