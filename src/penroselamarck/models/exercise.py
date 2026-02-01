"""
Exercise model.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :class:`Exercise`: Core unit of study (question/answer).

Attributes
----------
None

Examples
--------
>>> from penroselamarck.models.exercise import Exercise
>>> Exercise(question="hej", answer="hello", language="da")
Exercise(question='hej', answer='hello', language='da', tags=None, id=None, content_hash=None, created_at=None)

See Also
--------
:mod:`penroselamarck.mcp.server`
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Exercise(BaseModel):
    """
    Exercise(question, answer, language, tags=None, id=None) -> Exercise
    
    Concise (one-line) description of the function.

    Extended description of the function, if necessary.

    Parameters
    ----------
    question : str
        The prompt shown to the learner.
    answer : str
        The expected correct answer.
    language : str
        ISO 639-1 code (e.g., 'da' for Danish).
    tags : List[str], optional
        Labels such as 'vocab', 'grammar'.

    Returns
    -------
    Exercise
        The exercise object with optional identifiers.

    Examples
    --------
    >>> Exercise(question="hej", answer="hello", language="da")
    Exercise(question='hej', answer='hello', language='da', tags=None, id=None, content_hash=None, created_at=None)
    """
    question: str
    answer: str
    language: str
    tags: Optional[List[str]] = None
    id: Optional[str] = None
    content_hash: Optional[str] = None
    created_at: Optional[datetime] = None
