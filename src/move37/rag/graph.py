"""LangGraph wiring for note-grounded chat."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from move37.llm.openai import Move37OpenAIClient
from move37.rag.logging import log_event
from move37.rag.prompts import build_chat_messages
from move37.rag.retrieval import NoteRetrievalService


class ChatState(TypedDict):
    subject: str
    session_id: int
    content: str
    history: list[dict[str, str]]
    retrieved_chunks: list[dict[str, Any]]
    answer: str
    citations: list[dict[str, Any]]
    trace_id: str


class NotesChatGraph:
    """Run the LangGraph conversation workflow for notes chat."""

    def __init__(
        self,
        *,
        logger,
        retrieval_service: NoteRetrievalService | None = None,
        llm_client: Move37OpenAIClient | None = None,
    ) -> None:
        self.logger = logger
        self.retrieval_service = retrieval_service or NoteRetrievalService()
        self.llm_client = llm_client or self.retrieval_service.llm_client
        self.graph = self._build_graph()

    def invoke(self, state: ChatState) -> ChatState:
        return self.graph.invoke(state)

    def _build_graph(self):
        workflow = StateGraph(ChatState)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("answer", self._answer_node)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "answer")
        workflow.add_edge("answer", END)
        return workflow.compile()

    def _retrieve_node(self, state: ChatState) -> ChatState:
        start = datetime.now(timezone.utc)
        results = self.retrieval_service.search(subject=state["subject"], query=state["content"], top_k=8)
        latency_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        log_event(
            self.logger,
            service="move37-ai",
            subject=state["subject"],
            session_id=state["session_id"],
            trace_id=state["trace_id"],
            langgraph_node="retrieve",
            note_ids=[hit["noteId"] for hit in results],
            retrieved_chunk_ids=[hit["chunkId"] for hit in results],
            latency_ms=latency_ms,
            status="ok",
        )
        return {**state, "retrieved_chunks": results, "citations": results}

    def _answer_node(self, state: ChatState) -> ChatState:
        start = datetime.now(timezone.utc)
        answer = self.llm_client.chat(
            build_chat_messages(
                history=state["history"],
                content=state["content"],
                retrieved_chunks=state["retrieved_chunks"],
            )
        )
        latency_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        log_event(
            self.logger,
            service="move37-ai",
            subject=state["subject"],
            session_id=state["session_id"],
            trace_id=state["trace_id"],
            langgraph_node="answer",
            note_ids=[hit["noteId"] for hit in state["retrieved_chunks"]],
            retrieved_chunk_ids=[hit["chunkId"] for hit in state["retrieved_chunks"]],
            latency_ms=latency_ms,
            status="ok",
        )
        return {**state, "answer": answer}
