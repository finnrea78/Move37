"""
Exercise service.

Provides business logic for creating and listing exercises.

Public API
----------
- :class:`ExerciseService`: Exercise business operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.db.session import get_engine
>>> from penroselamarck.repositories.exercise_repository import ExerciseRepository
>>> service = ExerciseService(ExerciseRepository(get_engine()))
>>> callable(service.list_exercises)
True

See Also
--------
:mod:`penroselamarck.repositories.exercise_repository`
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime

from penroselamarck.repositories.exercise_repository import ExerciseRepository
from penroselamarck.services.errors import ConflictError, NotFoundError


class ExerciseService:
    """
    ExerciseService(exercise_repository) -> ExerciseService

    Concise (one-line) description of the service.

    Methods
    -------
    create_exercise(question, answer, language, tags)
        Create a new exercise with deduplication.
    list_exercises(language, tags, limit, offset)
        List exercises with optional filters.
    get_exercise(exercise_id)
        Fetch a single exercise.
    """

    def __init__(self, exercise_repository: ExerciseRepository) -> None:
        """
        __init__(exercise_repository) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        exercise_repository : ExerciseRepository
            Repository for exercise persistence.

        Returns
        -------
        None
            Initializes the service.
        """
        self._exercise_repository = exercise_repository

    def create_exercise(
        self,
        question: str,
        answer: str,
        language: str,
        tags: list[str] | None,
    ) -> dict:
        """
        create_exercise(question, answer, language, tags) -> Dict

        Concise (one-line) description of the function.

        Parameters
        ----------
        question : str
            Exercise prompt.
        answer : str
            Expected answer.
        language : str
            ISO 639-1 language code.
        tags : Optional[List[str]]
            Labels for the exercise.

        Returns
        -------
        Dict
            Summary of the created exercise.

        Throws
        ------
        ConflictError
            If an exercise with the same content already exists.
        """
        content_hash = self._content_hash(question, answer)
        if self._exercise_repository.exists_by_hash(content_hash):
            raise ConflictError("Duplicate exercise")
        exercise_id = uuid.uuid4().hex
        created_at = datetime.utcnow()
        self._exercise_repository.add_exercise(
            question=question,
            answer=answer,
            language=language,
            tags=tags,
            content_hash=content_hash,
            exercise_id=exercise_id,
            created_at=created_at,
        )
        return {
            "exerciseId": exercise_id,
            "question": question,
            "language": language,
            "tags": tags,
        }

    def list_exercises(
        self,
        language: str | None,
        tags: list[str] | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        """
        list_exercises(language, tags, limit, offset) -> List[Dict]

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : Optional[str]
            Language filter.
        tags : Optional[List[str]]
            Tag filter list.
        limit : int
            Maximum rows returned.
        offset : int
            Result offset.

        Returns
        -------
        List[Dict]
            Exercise summaries.
        """
        return self._exercise_repository.list_exercises(language, tags, limit, offset)

    def get_exercise(self, exercise_id: str) -> dict:
        """
        get_exercise(exercise_id) -> Dict

        Concise (one-line) description of the function.

        Parameters
        ----------
        exercise_id : str
            Identifier of the exercise.

        Returns
        -------
        Dict
            Exercise details.

        Throws
        ------
        NotFoundError
            If the exercise does not exist.
        """
        row = self._exercise_repository.get_exercise(exercise_id)
        if not row:
            raise NotFoundError("Exercise not found")
        return row

    def _content_hash(self, question: str, answer: str) -> str:
        """
        _content_hash(question, answer) -> str

        Concise (one-line) description of the function.

        Parameters
        ----------
        question : str
            The question text.
        answer : str
            The answer text.

        Returns
        -------
        str
            SHA-256 hex digest over normalized content.
        """
        canonical_q = " ".join(question.strip().split()).lower()
        canonical_a = " ".join(answer.strip().split()).lower()
        return hashlib.sha256((canonical_q + "\n" + canonical_a).encode("utf-8")).hexdigest()
