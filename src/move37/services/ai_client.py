"""HTTP client for the internal AI service."""

from __future__ import annotations

import os
from typing import Any

import httpx


class Move37AiClient:
    """Thin internal client for semantic search and chat generation."""

    def __init__(self, base_url: str | None = None, timeout: float = 60.0) -> None:
        self.base_url = (base_url or os.environ.get("MOVE37_AI_BASE_URL") or "http://move37-ai:8090").rstrip("/")
        self.timeout = timeout

    def search_notes(self, *, subject: str, query: str, top_k: int = 8) -> list[dict[str, Any]]:
        response = self._request(
            "POST",
            "/search",
            {"subject": subject, "query": query, "topK": top_k},
        )
        return list(response.get("results") or [])

    def send_chat_message(
        self,
        *,
        subject: str,
        session_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/chat",
            {"subject": subject, "sessionId": session_id, "content": content},
        )

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.request(method, path, json=payload)
            response.raise_for_status()
            return response.json()
