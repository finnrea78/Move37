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
>>> from penroselamarck.mcp.routers.mcp import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.mcp.transport`
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from penroselamarck.mcp.dependencies import get_mcp_transport
from penroselamarck.mcp.transport import McpHttpTransport

router = APIRouter()


@router.get("/mcp/sse")
async def mcp_sse(
    request: Request,
    transport: Annotated[McpHttpTransport, Depends(get_mcp_transport)],
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

    Returns
    -------
    StreamingResponse
        SSE stream for MCP messages.
    """
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

    Returns
    -------
    Dict
        Acknowledgement response.
    """
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    await transport.handle_post(session_id, payload)
    return {"status": "accepted"}
