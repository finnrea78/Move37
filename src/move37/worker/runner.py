"""Background worker that embeds notes into Milvus."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from move37.llm.openai import Move37OpenAIClient
from move37.langfuse.tracing import LangfuseTrace
from move37.models.note import NoteModel
from move37.repositories.note import NoteRepository
from move37.rag.logging import configure_logging, log_event
from move37.rag.retrieval import chunk_text
from move37.vectorstore.milvus import NoteMilvusStore


logger = configure_logging()


class EmbeddingWorker:
    """Poll Postgres jobs and keep Milvus in sync."""

    def __init__(self) -> None:
        database_url = os.environ.get("MOVE37_DATABASE_URL", "sqlite+pysqlite:///./move37.db")
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, future=True, connect_args=connect_args)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)
        self.milvus = NoteMilvusStore()
        self.llm_client = Move37OpenAIClient()
        self.poll_interval = float(os.environ.get("MOVE37_NOTES_WORKER_POLL_SECONDS", "2"))

    def run_forever(self) -> None:
        while True:
            processed = self.run_once()
            if not processed:
                time.sleep(self.poll_interval)

    def run_once(self) -> bool:
        with self.session_factory() as session:
            repository = NoteRepository(session)
            job = repository.claim_due_job()
            if job is None:
                session.rollback()
                return False
            trace = LangfuseTrace("note-embedding-job", {"note_id": job.note_id, "job_type": job.job_type})
            try:
                note: NoteModel | None = job.note
                if note is None:
                    job.status = "failed"
                    job.last_error = "Note not found."
                    session.commit()
                    return True
                start = datetime.now(timezone.utc)
                if job.job_type == "delete":
                    self.milvus.delete_note_chunks(note.id)
                else:
                    rows = self._build_rows(note)
                    self.milvus.replace_note_chunks(rows, note.id)
                    note.ingest_status = "ready"
                    note.ingest_error = None
                    note.last_embedded_at = datetime.now(timezone.utc)
                job.status = "completed"
                latency_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
                log_event(
                    logger,
                    service="move37-notes-worker",
                    subject=job.owner_subject,
                    session_id=None,
                    trace_id=trace.trace_id,
                    langgraph_node="embed_note",
                    note_ids=[note.id],
                    retrieved_chunk_ids=[],
                    latency_ms=latency_ms,
                    status="ok",
                )
                trace.end({"note_id": note.id, "job_id": job.id, "status": "completed"})
                session.commit()
            except Exception as error:  # pragma: no cover - runtime path
                if job.note is not None:
                    job.note.ingest_status = "failed" if job.attempt_count >= 3 else "pending"
                    job.note.ingest_error = str(error)
                job.status = "failed" if job.attempt_count >= 3 else "pending"
                job.last_error = str(error)
                job.run_after = datetime.now(timezone.utc) + timedelta(seconds=min(60, 5 * job.attempt_count))
                log_event(
                    logger,
                    service="move37-notes-worker",
                    subject=job.owner_subject,
                    session_id=None,
                    trace_id=trace.trace_id,
                    langgraph_node="embed_note",
                    note_ids=[job.note_id],
                    retrieved_chunk_ids=[],
                    latency_ms=0,
                    status="error",
                )
                trace.end({"job_id": job.id, "status": job.status, "error": str(error)})
                session.commit()
            return True

    def _build_rows(self, note: NoteModel) -> list[dict[str, object]]:
        chunks = chunk_text(note.body)
        embeddings = self.llm_client.embed_many([chunk["chunkText"] for chunk in chunks])
        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append(
                {
                    "chunk_id": f"note-{note.id}-chunk-{chunk['chunkIndex']}",
                    "owner_subject": note.owner_subject,
                    "note_id": note.id,
                    "note_title": note.title,
                    "linked_activity_id": note.linked_activity_id or "",
                    "source_type": note.source_type,
                    "source_filename": note.source_filename or "",
                    "chunk_index": chunk["chunkIndex"],
                    "chunk_text": chunk["chunkText"],
                    "content_sha256": note.content_sha256,
                    "embedding": embedding,
                }
            )
        return rows


def main() -> None:
    EmbeddingWorker().run_forever()


if __name__ == "__main__":
    main()
