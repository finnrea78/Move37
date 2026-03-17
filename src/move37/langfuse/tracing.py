"""Best-effort Langfuse helpers."""

from __future__ import annotations

import os
import uuid
from typing import Any

try:
    from langfuse import Langfuse
except Exception:  # pragma: no cover - optional dependency at runtime only
    Langfuse = None


class LangfuseTrace:
    """Small wrapper around Langfuse traces with graceful fallback."""

    def __init__(self, name: str, input_payload: dict[str, Any]) -> None:
        self.trace_id = str(uuid.uuid4())
        self._trace = None
        if Langfuse is None or not os.environ.get("LANGFUSE_SECRET_KEY") or not os.environ.get("LANGFUSE_PUBLIC_KEY"):
            return
        client = Langfuse(
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            host=os.environ.get("LANGFUSE_HOST"),
        )
        self._trace = client.trace(id=self.trace_id, name=name, input=input_payload)

    def span(self, name: str, input_payload: dict[str, Any] | None = None) -> Any:
        if self._trace is None:
            return None
        return self._trace.span(name=name, input=input_payload or {})

    def generation(self, name: str, input_payload: dict[str, Any] | None = None) -> Any:
        if self._trace is None:
            return None
        return self._trace.generation(name=name, input=input_payload or {})

    def end(self, output_payload: dict[str, Any] | None = None) -> None:
        if self._trace is not None:
            self._trace.update(output=output_payload or {})
