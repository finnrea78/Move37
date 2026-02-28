"""Provider-agnostic ports for orchestrator dependencies.

Ports define the interfaces consumed by orchestration workflows. Concrete
adapters (OpenAI, GitHub, SQLAlchemy, tool runners, research engines) should
implement these protocols.
"""

from penroselamarck.orchestrator.ports.research import ResearchClient, ResearchDocument
from penroselamarck.orchestrator.ports.steps import Classifier, Extractor, Scorer, TransientStepError
from penroselamarck.orchestrator.ports.storage import WorkflowStore
from penroselamarck.orchestrator.ports.tools import ToolInvocation, ToolResult, ToolRuntime

__all__ = [
    "TransientStepError",
    "Extractor",
    "Classifier",
    "Scorer",
    "WorkflowStore",
    "ResearchClient",
    "ResearchDocument",
    "ToolRuntime",
    "ToolInvocation",
    "ToolResult",
]
