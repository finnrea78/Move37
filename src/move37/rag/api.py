"""Internal RAG service API for semantic search and note-grounded chat."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from move37.langfuse.tracing import LangfuseTrace
from move37.repositories.note import ChatRepository
from move37.rag.graph import NotesChatGraph
from move37.rag.logging import configure_logging
from move37.rag.retrieval import NoteRetrievalService


logger = configure_logging()


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    query: str = Field(min_length=1)
    topK: int = Field(default=8, ge=1, le=20)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    sessionId: int
    content: str = Field(min_length=1)


class RagRuntime:
    """Run semantic search and LangGraph-based chat."""

    def __init__(self) -> None:
        database_url = os.environ.get("MOVE37_DATABASE_URL", "sqlite+pysqlite:///./move37.db")
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, future=True, connect_args=connect_args)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)
        self.retrieval_service = NoteRetrievalService()
        self.chat_graph = NotesChatGraph(logger=logger, retrieval_service=self.retrieval_service)

    def search(self, subject: str, query: str, top_k: int) -> list[dict[str, Any]]:
        return self.retrieval_service.search(subject=subject, query=query, top_k=top_k)

    def chat(self, subject: str, session_id: int, content: str) -> dict[str, Any]:
        trace = LangfuseTrace(
            "notes-chat",
            {"subject": subject, "session_id": session_id, "content": content},
        )
        with self.session_factory() as session:
            repository = ChatRepository(session)
            chat_session = repository.get_session(subject, session_id)
            if chat_session is None:
                raise HTTPException(status_code=404, detail="Chat session not found.")
            history = [
                {"role": message.role, "content": message.content}
                for message in chat_session.messages[-12:]
            ]
            user_message = repository.append_message(chat_session, role="user", content=content)
            session.commit()

        result = self.chat_graph.invoke(
            {
                "subject": subject,
                "session_id": session_id,
                "content": content,
                "history": history,
                "retrieved_chunks": [],
                "answer": "",
                "citations": [],
                "trace_id": trace.trace_id,
            }
        )

        with self.session_factory() as session:
            repository = ChatRepository(session)
            chat_session = repository.get_session(subject, session_id)
            if chat_session is None:
                raise HTTPException(status_code=404, detail="Chat session not found.")
            assistant_message = repository.append_message(
                chat_session,
                role="assistant",
                content=result["answer"],
                citations=result["citations"],
                trace_id=result["trace_id"],
            )
            session.commit()
            trace.end({"citations": result["citations"], "assistant_message_id": assistant_message.id})
            return {
                "userMessage": {
                    "id": user_message.id,
                    "role": "user",
                    "content": user_message.content,
                    "citations": [],
                    "traceId": trace.trace_id,
                    "createdAt": user_message.created_at.isoformat(),
                },
                "assistantMessage": {
                    "id": assistant_message.id,
                    "role": "assistant",
                    "content": assistant_message.content,
                    "citations": assistant_message.citations_json,
                    "traceId": assistant_message.trace_id,
                    "createdAt": assistant_message.created_at.isoformat(),
                },
            }


def create_app() -> FastAPI:
    runtime = RagRuntime()
    app = FastAPI(title="Move37 RAG", version="0.1.0")
    app.state.runtime = runtime

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/search")
    def search(payload: SearchRequest) -> dict[str, Any]:
        return {"results": runtime.search(payload.subject, payload.query, payload.topK)}

    @app.post("/chat")
    def chat(payload: ChatRequest) -> dict[str, Any]:
        return runtime.chat(payload.subject, payload.sessionId, payload.content)

    return app


app = create_app()
