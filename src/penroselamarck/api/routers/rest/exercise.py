"""
Exercise REST endpoints.

Defines routes for creating and listing exercises.

Public API
----------
- :data:`router`: FastAPI router for exercise endpoints.

Attributes
----------
router : APIRouter
    Router exposing exercise endpoints.

Examples
--------
>>> from penroselamarck.api.routers.rest.exercise import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.exercise_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from penroselamarck.api.dependencies import get_service_container
from penroselamarck.api.schemas import ExerciseCreateInput, ExerciseListFilters, ExerciseListItem
from penroselamarck.services.container import ServiceContainer
from penroselamarck.services.errors import ConflictError

router = APIRouter()


@router.post("/exercise", response_model=ExerciseListItem)
def exercise_create(
    payload: ExerciseCreateInput,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ExerciseListItem:
    """
    exercise_create(payload, services) -> ExerciseListItem

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : ExerciseCreateInput
        Fields to create an exercise.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    ExerciseListItem
        A summary of the created exercise.
    """
    try:
        row = services.exercise_service.create_exercise(
            question=payload.question,
            answer=payload.answer,
            language=payload.language,
            tags=payload.tags,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    return ExerciseListItem(**row)


@router.get("/exercise", response_model=list[ExerciseListItem])
def exercise_list(
    filters: Annotated[ExerciseListFilters, Depends()],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> list[ExerciseListItem]:
    """
    exercise_list(filters, services) -> List[ExerciseListItem]

    Concise (one-line) description of the function.

    Parameters
    ----------
    filters : ExerciseListFilters
        Query filters for exercises.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    List[ExerciseListItem]
        Exercise summaries matching the filters.
    """
    rows = services.exercise_service.list_exercises(
        language=filters.language,
        tags=filters.tags,
        limit=filters.limit or 50,
        offset=filters.offset or 0,
    )
    return [ExerciseListItem(**row) for row in rows]
