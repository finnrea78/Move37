"""
Authentication REST endpoints.

Defines REST routes for login and user context.

Public API
----------
- :data:`router`: FastAPI router for auth endpoints.

Attributes
----------
router : APIRouter
    Router exposing authentication endpoints.

Examples
--------
>>> from penroselamarck.mcp.routers.rest.auth import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.auth_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from penroselamarck.mcp.dependencies import get_service_container
from penroselamarck.mcp.schemas import LoginInput, LoginOutput
from penroselamarck.services.container import ServiceContainer
from penroselamarck.services.errors import ServiceError

router = APIRouter()


@router.post("/auth/login", response_model=LoginOutput)
def auth_login(
    payload: LoginInput,
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> LoginOutput:
    """
    auth_login(payload, services) -> LoginOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : LoginInput
        Token used to authenticate the user.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    LoginOutput
        Authenticated user information.
    """
    try:
        user = services.auth_service.login(payload.token)
    except ServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc
    return LoginOutput(userId=user.user_id, roles=user.roles)


@router.get("/auth/me", response_model=LoginOutput)
def auth_me(
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> LoginOutput:
    """
    auth_me(services) -> LoginOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    LoginOutput
        The current user context (demo user).
    """
    user = services.auth_service.demo_user()
    return LoginOutput(userId=user.user_id, roles=user.roles)
