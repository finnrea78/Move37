"""Tool runtime port for agentic workflow execution.

Future orchestrator nodes can call tools (code search, web research,
static analysis, repository graph queries) through this provider-neutral API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ToolInvocation:
    """Tool call request payload."""

    name: str
    arguments: dict


@dataclass(frozen=True)
class ToolResult:
    """Tool call result payload."""

    success: bool
    output: str
    metadata: dict[str, str] | None = None


class ToolRuntime(Protocol):
    """Execute named tools with structured arguments."""

    def invoke(self, invocation: ToolInvocation) -> ToolResult:
        """Execute one tool invocation and return the normalized result."""
