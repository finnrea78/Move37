"""MCP transport endpoints for Move37."""

from __future__ import annotations

from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from move37.api.dependencies import (
    get_current_subject_mcp,
    get_mcp_transport,
)
from move37.api.transport import McpHttpTransport

router = APIRouter()


@router.get("/mcp/sse")
async def mcp_sse(
    request: Request,
    transport: Annotated[McpHttpTransport, Depends(get_mcp_transport)],
    subject: Annotated[str, Depends(get_current_subject_mcp)],
):
    del subject
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
    subject: Annotated[str, Depends(get_current_subject_mcp)],
) -> dict[str, str]:
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    await transport.handle_post(session_id, payload, subject)
    return {"status": "accepted"}


@router.post("/mcp/sse")
async def mcp_streamable_http(
    request: Request,
    transport: Annotated[McpHttpTransport, Depends(get_mcp_transport)],
    subject: Annotated[str, Depends(get_current_subject_mcp)],
) -> JSONResponse:
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    response = transport.handle_request(payload, subject)
    if response is None:
        return JSONResponse(status_code=202, content={"status": "accepted"})
    return JSONResponse(content=response)
