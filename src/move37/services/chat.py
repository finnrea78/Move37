"""Chat session service."""

from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from move37.repositories.note import ChatRepository
from move37.services.ai_client import Move37AiClient
from move37.services.errors import NotFoundError


class ChatSessionService:
    """Own chat session persistence and AI service forwarding."""

    def __init__(self, session_factory: sessionmaker, ai_client: Move37AiClient) -> None:
        self._session_factory = session_factory
        self._ai_client = ai_client

    def create_session(self, subject: str, title: str | None = None) -> dict[str, object]:
        with self._session_factory() as session:
            repository = ChatRepository(session)
            chat_session = repository.create_session(subject, title or "Notes chat")
            session.commit()
            session.refresh(chat_session)
            return repository.serialize_session(chat_session)

    def get_session(self, subject: str, session_id: int) -> dict[str, object]:
        with self._session_factory() as session:
            repository = ChatRepository(session)
            chat_session = repository.get_session(subject, session_id)
            if chat_session is None:
                raise NotFoundError("Chat session not found.")
            return repository.serialize_session(chat_session)

    def send_message(self, subject: str, session_id: int, content: str) -> dict[str, object]:
        with self._session_factory() as session:
            repository = ChatRepository(session)
            chat_session = repository.get_session(subject, session_id)
            if chat_session is None:
                raise NotFoundError("Chat session not found.")
        return self._ai_client.send_chat_message(subject=subject, session_id=session_id, content=content)
