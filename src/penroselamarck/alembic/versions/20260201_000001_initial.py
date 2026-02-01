"""
Initial schema: exercises, practice_sessions, attempts

Revision ID: 20260201_000001
Revises: 
Create Date: 2026-02-01 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260201_000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Apply the initial schema.
    """
    op.create_table(
        'exercises',
        sa.Column('id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=8), nullable=False, index=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('content_hash', name='uq_exercises_content_hash'),
    )
    # Add explicit indexes (since index=True on Column isn't applied here)
    op.create_index('ix_exercises_language', 'exercises', ['language'])
    op.create_index('ix_exercises_content_hash', 'exercises', ['content_hash'])

    op.create_table(
        'practice_sessions',
        sa.Column('session_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('language', sa.String(length=8), nullable=False),
        sa.Column('strategy', sa.String(length=32), nullable=False),
        sa.Column('target_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('selected_exercise_ids', sa.JSON(), nullable=True),
    )

    op.create_table(
        'attempts',
        sa.Column('id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('exercise_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('user_answer', sa.Text(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('evaluated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_attempts_session_id', 'attempts', ['session_id'])
    op.create_index('ix_attempts_exercise_id', 'attempts', ['exercise_id'])


def downgrade() -> None:
    """
    Drop all initial schema tables.
    """
    op.drop_index('ix_attempts_exercise_id', table_name='attempts')
    op.drop_index('ix_attempts_session_id', table_name='attempts')
    op.drop_table('attempts')
    op.drop_table('practice_sessions')
    op.drop_index('ix_exercises_content_hash', table_name='exercises')
    op.drop_index('ix_exercises_language', table_name='exercises')
    op.drop_table('exercises')
