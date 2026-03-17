"""FastAPI dependency helpers for Move37."""

from __future__ import annotations

import os

from fastapi import HTTPException, Request, status

from move37.api.transport import McpHttpTransport
from move37.services.container import ServiceContainer


def get_service_container(request: Request) -> ServiceContainer:
    """Return the application service container."""

    return request.app.state.services


def get_current_subject(request: Request) -> str:
    """Validate the bearer token and return the active subject."""

    expected_token = os.environ.get("MOVE37_API_BEARER_TOKEN", "move37-dev-token")
    expected_subject = os.environ.get("MOVE37_API_BEARER_SUBJECT", "local-user")
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return expected_subject


def get_mcp_transport(request: Request) -> McpHttpTransport:
    """Return the configured MCP transport."""

    return request.app.state.mcp_transport


def get_current_subject_mcp(request: Request) -> str:
    """Authenticate MCP requests using the same bearer flow as REST."""

    return get_current_subject(request)
