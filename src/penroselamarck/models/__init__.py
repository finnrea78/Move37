"""
penroselamarck.models package

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :mod:`penroselamarck.models.exercise_orm`
- :mod:`penroselamarck.models.practice_session_orm`
- :mod:`penroselamarck.models.attempt_orm`
- :mod:`penroselamarck.models.exercise` (Pydantic schema)
- :mod:`penroselamarck.models.practice_session` (Pydantic schema)
- :mod:`penroselamarck.models.attempt` (Pydantic schema)
"""

# Ensure ORM metadata is imported for Alembic discovery
from .base import Base  # noqa: F401

# Re-export Pydantic schemas for convenience (optional)
from .exercise import Exercise  # noqa: F401
from .practice_session import PracticeSession  # noqa: F401
from .attempt import Attempt  # noqa: F401
