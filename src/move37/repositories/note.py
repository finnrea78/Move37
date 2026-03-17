"""Repositories for notes, embedding jobs, and chat sessions."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from move37.models.chat import ChatMessageModel, ChatSessionModel
from move37.models.note import NoteEmbeddingJobModel, NoteModel


class NoteRepository:
    """Persist and retrieve notes and embedding jobs."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_note(
        self,
        *,
        owner_subject: str,
        title: str,
        body: str,
        source_type: str,
        source_filename: str | None,
        linked_activity_id: str | None,
        content_sha256: str,
        ingest_status: str = "pending",
    ) -> NoteModel:
        note = NoteModel(
            owner_subject=owner_subject,
            title=title,
            body=body,
            source_type=source_type,
            source_filename=source_filename,
            linked_activity_id=linked_activity_id,
            content_sha256=content_sha256,
            ingest_status=ingest_status,
        )
        self._session.add(note)
        self._session.flush()
        return note

    def get_note(self, subject: str, note_id: int) -> NoteModel | None:
        return (
            self._session.query(NoteModel)
            .filter(NoteModel.owner_subject == subject, NoteModel.id == note_id)
            .one_or_none()
        )

    def get_note_by_linked_activity(self, subject: str, activity_id: str) -> NoteModel | None:
        return (
            self._session.query(NoteModel)
            .filter(NoteModel.owner_subject == subject, NoteModel.linked_activity_id == activity_id)
            .one_or_none()
        )

    def list_notes(self, subject: str) -> list[NoteModel]:
        return (
            self._session.query(NoteModel)
            .filter(NoteModel.owner_subject == subject)
            .order_by(NoteModel.updated_at.desc(), NoteModel.id.desc())
            .all()
        )

    def enqueue_job(
        self,
        *,
        note_id: int,
        owner_subject: str,
        job_type: str,
        run_after: datetime | None = None,
    ) -> NoteEmbeddingJobModel:
        job = NoteEmbeddingJobModel(
            note_id=note_id,
            owner_subject=owner_subject,
            job_type=job_type,
            status="pending",
            run_after=run_after,
        )
        self._session.add(job)
        self._session.flush()
        return job

    def claim_due_job(self) -> NoteEmbeddingJobModel | None:
        now = datetime.now(timezone.utc)
        job = (
            self._session.query(NoteEmbeddingJobModel)
            .options(selectinload(NoteEmbeddingJobModel.note))
            .filter(
                NoteEmbeddingJobModel.status == "pending",
                or_(NoteEmbeddingJobModel.run_after.is_(None), NoteEmbeddingJobModel.run_after <= now),
            )
            .order_by(NoteEmbeddingJobModel.created_at.asc(), NoteEmbeddingJobModel.id.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if job is None:
            return None
        job.status = "processing"
        job.attempt_count += 1
        self._session.flush()
        return job

    @staticmethod
    def serialize_note(note: NoteModel) -> dict[str, object]:
        return {
            "id": note.id,
            "title": note.title,
            "body": note.body,
            "sourceType": note.source_type,
            "sourceFilename": note.source_filename,
            "linkedActivityId": note.linked_activity_id,
            "ingestStatus": note.ingest_status,
            "ingestError": note.ingest_error,
            "contentSha256": note.content_sha256,
            "lastEmbeddedAt": note.last_embedded_at.isoformat() if note.last_embedded_at else None,
            "createdAt": note.created_at.isoformat(),
            "updatedAt": note.updated_at.isoformat(),
        }


class ChatRepository:
    """Persist and retrieve chat sessions and messages."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_session(self, subject: str, title: str) -> ChatSessionModel:
        session = ChatSessionModel(owner_subject=subject, title=title)
        self._session.add(session)
        self._session.flush()
        return session

    def get_session(self, subject: str, session_id: int) -> ChatSessionModel | None:
        return (
            self._session.query(ChatSessionModel)
            .options(selectinload(ChatSessionModel.messages))
            .filter(ChatSessionModel.owner_subject == subject, ChatSessionModel.id == session_id)
            .one_or_none()
        )

    def list_messages(self, subject: str, session_id: int) -> list[ChatMessageModel]:
        session = self.get_session(subject, session_id)
        return session.messages if session else []

    def append_message(
        self,
        chat_session: ChatSessionModel,
        *,
        role: str,
        content: str,
        citations: list[dict[str, object]] | None = None,
        trace_id: str | None = None,
    ) -> ChatMessageModel:
        message = ChatMessageModel(
            session_id=chat_session.id,
            role=role,
            content=content,
            citations_json=citations or [],
            trace_id=trace_id,
        )
        self._session.add(message)
        chat_session.last_message_at = datetime.now(timezone.utc)
        self._session.flush()
        return message

    @staticmethod
    def serialize_session(session: ChatSessionModel) -> dict[str, object]:
        return {
            "id": session.id,
            "title": session.title,
            "lastMessageAt": session.last_message_at.isoformat() if session.last_message_at else None,
            "createdAt": session.created_at.isoformat(),
            "updatedAt": session.updated_at.isoformat(),
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "citations": message.citations_json,
                    "traceId": message.trace_id,
                    "createdAt": message.created_at.isoformat(),
                }
                for message in session.messages
            ],
        }
