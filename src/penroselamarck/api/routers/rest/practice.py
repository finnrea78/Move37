"""
Practice REST endpoints.

Defines routes for practice session workflow.

Public API
----------
- :data:`router`: FastAPI router for practice endpoints.

Attributes
----------
router : APIRouter
    Router exposing practice endpoints.

Examples
--------
>>> from penroselamarck.api.routers.rest.practice import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.practice_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from penroselamarck.api.dependencies import get_service_container
from penroselamarck.api.schemas import (
    ExerciseListItem,
    PracticeStartInput,
    PracticeStartOutput,
    PracticeSubmitInput,
    PracticeSubmitOutput,
)
from penroselamarck.services.container import ServiceContainer
from penroselamarck.services.errors import NoContentError, NotFoundError

router = APIRouter()


@router.post("/practice/start", response_model=PracticeStartOutput)
def practice_start(
    payload: PracticeStartInput,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> PracticeStartOutput:
    """
    practice_start(payload, services) -> PracticeStartOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : PracticeStartInput
        Session start payload.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    PracticeStartOutput
        Session creation summary.
    """
    result = services.practice_service.start(
        language=payload.language,
        count=payload.count,
        strategy=payload.strategy,
    )
    return PracticeStartOutput(**result)


@router.get("/practice/next", response_model=ExerciseListItem)
def practice_next(
    sessionId: str,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ExerciseListItem:
    """
    practice_next(sessionId, services) -> ExerciseListItem

    Concise (one-line) description of the function.

    Parameters
    ----------
    sessionId : str
        Session identifier.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    ExerciseListItem
        Next exercise summary.
    """
    try:
        row = services.practice_service.next(sessionId)
    except NoContentError as exc:
        raise HTTPException(status_code=204, detail=exc.message) from exc
    return ExerciseListItem(**row)


@router.post("/practice/submit", response_model=PracticeSubmitOutput)
def practice_submit(
    payload: PracticeSubmitInput,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> PracticeSubmitOutput:
    """
    practice_submit(payload, services) -> PracticeSubmitOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : PracticeSubmitInput
        Practice submission payload.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    PracticeSubmitOutput
        Submission evaluation response.
    """
    try:
        result = services.practice_service.submit(
            session_id=payload.sessionId,
            exercise_id=payload.exerciseId,
            user_answer=payload.userAnswer,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return PracticeSubmitOutput(**result)


@router.post("/practice/end")
def practice_end(
    sessionId: str,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> dict:
    """
    practice_end(sessionId, services) -> Dict

    Concise (one-line) description of the function.

    Parameters
    ----------
    sessionId : str
        Session identifier.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    Dict
        Session summary metrics.
    """
    return services.practice_service.end(sessionId)
