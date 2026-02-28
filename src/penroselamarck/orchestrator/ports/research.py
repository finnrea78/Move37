"""Online research port for future agentic orchestration flows.

The orchestrator can use this port to augment extraction/classification with
external sources (for example repository issues, standards pages, or docs).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ResearchDocument:
    """One normalized research result from an external source."""

    title: str
    url: str
    snippet: str
    source: str


class ResearchClient(Protocol):
    """Provider-neutral interface for online research retrieval."""

    def search(self, query: str, max_results: int = 5) -> list[ResearchDocument]:
        """Return ranked research documents for the query."""
