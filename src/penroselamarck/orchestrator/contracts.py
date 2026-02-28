"""Backward-compatible contracts facade.

Prefer importing interfaces from ``penroselamarck.orchestrator.ports`` in new
code. This module remains for compatibility with existing imports.
"""

from penroselamarck.orchestrator.ports import (
    Classifier,
    Extractor,
    Scorer,
    TransientStepError,
    WorkflowStore,
)

# Backward-compatible aliases for previous naming.
ExtractorPort = Extractor
ClassifierPort = Classifier
ScorerPort = Scorer
WorkflowStorePort = WorkflowStore

__all__ = [
    "TransientStepError",
    "Extractor",
    "Classifier",
    "Scorer",
    "WorkflowStore",
    "ExtractorPort",
    "ClassifierPort",
    "ScorerPort",
    "WorkflowStorePort",
]
