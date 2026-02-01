"""
PerformanceSummary model.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :class:`PerformanceSummary`: Aggregated stats for exercises.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PerformanceSummary(BaseModel):
    """
    PerformanceSummary(exercise_id, total_attempts, pass_rate, last_practiced_at) -> PerformanceSummary

    Concise (one-line) description of the function.

    Parameters
    ----------
    exercise_id : str
        Identifier of the exercise.
    total_attempts : int
        Total attempts recorded.
    pass_rate : float
        Ratio of passed attempts in [0, 1].
    last_practiced_at : datetime
        Timestamp of last practice.

    Returns
    -------
    PerformanceSummary
        Aggregated performance statistics for an exercise.
    """
    exercise_id: str
    total_attempts: int
    pass_rate: float
    last_practiced_at: Optional[datetime] = None
