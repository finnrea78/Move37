"""
Study context REST endpoints.

Defines REST routes for managing the active study context.

Public API
----------
- :data:`router`: FastAPI router for context endpoints.

Attributes
----------
router : APIRouter
    Router exposing context endpoints.

Examples
--------
>>> from penroselamarck.api.routers.rest.context import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.context_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from penroselamarck.api.dependencies import get_service_container
from penroselamarck.api.schemas import ContextInput, ContextOutput
from penroselamarck.services.container import ServiceContainer

router = APIRouter()


@router.post("/study/context", response_model=ContextOutput)
def set_context(
    payload: ContextInput,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ContextOutput:
    """
    set_context(payload, services) -> ContextOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : ContextInput
        The study language to set.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    ContextOutput
        The active context identifier and language.
    """
    state = services.context_service.set_context(payload.language)
    return ContextOutput(activeContextId=state.active_context_id, language=state.language)


@router.get("/study/context", response_model=ContextOutput)
def get_context(
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> ContextOutput:
    """
    get_context(services) -> ContextOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    ContextOutput
        Returns the active context and language for user.
    """
    state = services.context_service.get_context()
    return ContextOutput(activeContextId=state.active_context_id, language=state.language)
