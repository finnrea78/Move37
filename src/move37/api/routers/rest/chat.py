"""Chat endpoints for the Move37 API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from httpx import HTTPError

from move37.api.dependencies import get_current_subject, get_service_container
from move37.api.schemas import (
    ChatMessageCreateInput,
    ChatMessageResponse,
    ChatMessageOutput,
    ChatSessionCreateInput,
    ChatSessionOutput,
)
from move37.services.container import ServiceContainer
from move37.services.errors import NotFoundError

router = APIRouter(tags=["chat"])


def _handle_chat_error(error: Exception) -> None:
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=error.message) from error
    if isinstance(error, HTTPError):
        raise HTTPException(status_code=503, detail="AI service unavailable.") from error
    raise error


@router.post("/chat/sessions", response_model=ChatSessionOutput)
def create_session(
    payload: ChatSessionCreateInput,
    subject: Annotated[str, Depends(get_current_subject)],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ChatSessionOutput:
    response = services.chat_session_service.create_session(subject, payload.title)
    return ChatSessionOutput(**response)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionOutput)
def get_session(
    session_id: int,
    subject: Annotated[str, Depends(get_current_subject)],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ChatSessionOutput:
    try:
        response = services.chat_session_service.get_session(subject, session_id)
    except Exception as error:  # pragma: no cover
        _handle_chat_error(error)
    return ChatSessionOutput(**response)


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(
    session_id: int,
    payload: ChatMessageCreateInput,
    subject: Annotated[str, Depends(get_current_subject)],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ChatMessageResponse:
    try:
        response = services.chat_session_service.send_message(subject, session_id, payload.content)
    except Exception as error:  # pragma: no cover
        _handle_chat_error(error)
    return ChatMessageResponse(
        userMessage=ChatMessageOutput(**response["userMessage"]),
        assistantMessage=ChatMessageOutput(**response["assistantMessage"]),
    )
