"""Add notes, embedding jobs, and chat persistence.

Revision ID: 20260316_000003
Revises: 20260316_000002
Create Date: 2026-03-16 00:00:03
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260316_000003"
down_revision = "20260316_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activity_nodes",
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="activity"),
    )
    op.add_column(
        "activity_nodes",
        sa.Column("linked_note_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_activity_nodes_linked_note_id", "activity_nodes", ["linked_note_id"])

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("owner_subject", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_type", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("source_filename", sa.String(length=255), nullable=True),
        sa.Column("linked_activity_id", sa.String(length=255), nullable=True),
        sa.Column("ingest_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("ingest_error", sa.Text(), nullable=True),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("last_embedded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notes_owner_subject", "notes", ["owner_subject"])
    op.create_index("ix_notes_linked_activity_id", "notes", ["linked_activity_id"])

    op.create_table(
        "note_embedding_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("owner_subject", sa.String(length=255), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False, server_default="upsert"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("run_after", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_note_embedding_jobs_note_id", "note_embedding_jobs", ["note_id"])
    op.create_index("ix_note_embedding_jobs_owner_subject", "note_embedding_jobs", ["owner_subject"])
    op.create_index("ix_note_embedding_jobs_status", "note_embedding_jobs", ["status"])
    op.create_index("ix_note_embedding_jobs_run_after", "note_embedding_jobs", ["run_after"])

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("owner_subject", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Notes chat"),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_chat_sessions_owner_subject", "chat_sessions", ["owner_subject"])
    op.create_index("ix_chat_sessions_last_message_at", "chat_sessions", ["last_message_at"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("trace_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])
    op.create_index("ix_chat_messages_trace_id", "chat_messages", ["trace_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_trace_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_last_message_at", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_owner_subject", table_name="chat_sessions")
    op.drop_table("chat_sessions")
    op.drop_index("ix_note_embedding_jobs_run_after", table_name="note_embedding_jobs")
    op.drop_index("ix_note_embedding_jobs_status", table_name="note_embedding_jobs")
    op.drop_index("ix_note_embedding_jobs_owner_subject", table_name="note_embedding_jobs")
    op.drop_index("ix_note_embedding_jobs_note_id", table_name="note_embedding_jobs")
    op.drop_table("note_embedding_jobs")
    op.drop_index("ix_notes_linked_activity_id", table_name="notes")
    op.drop_index("ix_notes_owner_subject", table_name="notes")
    op.drop_table("notes")
    op.drop_index("ix_activity_nodes_linked_note_id", table_name="activity_nodes")
    op.drop_column("activity_nodes", "linked_note_id")
    op.drop_column("activity_nodes", "kind")
