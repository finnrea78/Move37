"""Retrieval and chunking helpers for note-grounded chat."""

from __future__ import annotations

from typing import Any

import tiktoken

from move37.llm.openai import Move37OpenAIClient
from move37.vectorstore.milvus import NoteMilvusStore


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 120) -> list[dict[str, Any]]:
    """Split a note body into overlapping token chunks."""

    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text or "")
    if not tokens:
        return [{"chunkIndex": 0, "chunkText": ""}]
    step = max(1, chunk_size - overlap)
    chunks: list[dict[str, Any]] = []
    for index, start in enumerate(range(0, len(tokens), step)):
        chunk_tokens = tokens[start : start + chunk_size]
        chunks.append(
            {
                "chunkIndex": index,
                "chunkText": encoder.decode(chunk_tokens),
            }
        )
        if start + chunk_size >= len(tokens):
            break
    return chunks


class NoteRetrievalService:
    """Embed queries and retrieve note chunks from Milvus."""

    def __init__(
        self,
        llm_client: Move37OpenAIClient | None = None,
        vectorstore: NoteMilvusStore | None = None,
    ) -> None:
        self.llm_client = llm_client or Move37OpenAIClient()
        self.vectorstore = vectorstore or NoteMilvusStore()

    def search(self, *, subject: str, query: str, top_k: int = 8) -> list[dict[str, Any]]:
        embedding = self.llm_client.embed_one(query)
        return self.vectorstore.search(subject=subject, embedding=embedding, top_k=top_k)
