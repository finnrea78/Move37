"""
PracticeSession model.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :class:`PracticeSession`: A session selecting and sequencing exercises.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PracticeSession(BaseModel):
    """
    PracticeSession(session_id, language, strategy, target_count, status) -> PracticeSession
    
    Concise (one-line) description of the function.

    Parameters
    ----------
    session_id : str
        Unique identifier for the session.
    language : str
        The active language for practice.
    strategy : str
        Selection strategy ('weakest'|'spaced'|'mixed').
    target_count : int
        Number of exercises requested.
    status : str
        Lifecycle status ('started'|'ended').

    Returns
    -------
    PracticeSession
        The session record.
    """
    session_id: str
    language: str
    strategy: str
    target_count: int
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    selected_exercise_ids: Optional[List[str]] = None
