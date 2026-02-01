"""
Attempt model.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :class:`Attempt`: A user's answer evaluation record.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Attempt(BaseModel):
    """
    Attempt(session_id, exercise_id, user_answer, score, passed) -> Attempt

    Concise (one-line) description of the function.

    Parameters
    ----------
    session_id : str
        Identifier of the session.
    exercise_id : str
        Identifier of the exercise.
    user_answer : str
        The learner's answer.
    score : float
        Evaluation score in [0, 1].
    passed : bool
        Whether the answer meets the passing threshold.

    Returns
    -------
    Attempt
        The attempt record.
    """
    session_id: str
    exercise_id: str
    user_answer: str
    score: float
    passed: bool
    evaluated_at: Optional[datetime] = None
