"""
MCP transport endpoints.

Defines HTTP/SSE endpoints for MCP JSON-RPC traffic.

Public API
----------
- :data:`router`: FastAPI router for MCP transport.

Attributes
----------
router : APIRouter
    Router exposing MCP transport endpoints.

Examples
--------
>>> from penroselamarck.api.routers.mcp import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.api.transport`
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from penroselamarck.api.dependencies import get_mcp_transport, get_service_container
from penroselamarck.api.transport import McpHttpTransport
from penroselamarck.services.container import ServiceContainer
from penroselamarck.services.errors import ServiceError

router = APIRouter()


def _resource_metadata_url(request: Request) -> str:
    """
    _resource_metadata_url(request) -> str

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.

    Returns
    -------
    str
        Resource metadata URL for OAuth discovery.

    Examples
    --------
    >>> isinstance(_resource_metadata_url.__name__, str)
    True
    """
    return f"{str(request.base_url).rstrip('/')}/.well-known/oauth-protected-resource"


def _www_authenticate_header(request: Request, description: str) -> str:
    """
    _www_authenticate_header(request, description) -> str

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.
    description : str
        Error description for the header.

    Returns
    -------
    str
        WWW-Authenticate header value.

    Examples
    --------
    >>> isinstance(_www_authenticate_header.__name__, str)
    True
    """
    safe_description = description.replace('"', "'")
    resource_metadata = _resource_metadata_url(request)
    return (
        'Bearer realm="mcp", error="invalid_token", '
        f'error_description="{safe_description}", '
        f'resource_metadata="{resource_metadata}"'
    )


def _require_bearer_token(
    request: Request,
    services: ServiceContainer,
) -> None:
    """
    _require_bearer_token(request, services) -> None

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.
    services : ServiceContainer
        Service container dependency.

    Throws
    ------
    HTTPException
        Raised when authentication fails.

    Returns
    -------
    None
        Validates the bearer token or raises an HTTP exception.

    Examples
    --------
    >>> callable(_require_bearer_token)
    True
    """
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={
                "WWW-Authenticate": _www_authenticate_header(request, "Missing bearer token.")
            },
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header.",
            headers={
                "WWW-Authenticate": _www_authenticate_header(
                    request, "Invalid authorization header."
                )
            },
        )
    try:
        services.auth_service.login(token)
    except ServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": _www_authenticate_header(request, exc.message)},
        ) from exc


@router.get("/mcp/sse")
async def mcp_sse(
    request: Request,
    transport: Annotated[McpHttpTransport, Depends(get_mcp_transport)],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
):
    """
    mcp_sse(request, transport) -> StreamingResponse

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.
    transport : McpHttpTransport
        MCP transport dependency.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    StreamingResponse
        SSE stream for MCP messages.
    """
    _require_bearer_token(request, services)
    if not request.url.path.endswith("/mcp/sse"):
        raise HTTPException(status_code=400, detail="Invalid SSE path")
    endpoint_base = request.url.path[: -len("/sse")]
    endpoint_path = f"{endpoint_base}/messages"
    return await transport.sse_endpoint(request, endpoint_path)


@router.post("/mcp/messages", status_code=202)
async def mcp_messages(
    request: Request,
    session_id: str,
    transport: Annotated[McpHttpTransport, Depends(get_mcp_transport)],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> dict:
    """
    mcp_messages(request, session_id, transport) -> Dict

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.
    session_id : str
        MCP session identifier.
    transport : McpHttpTransport
        MCP transport dependency.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    Dict
        Acknowledgement response.
    """
    _require_bearer_token(request, services)
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    await transport.handle_post(session_id, payload)
    return {"status": "accepted"}
