"""MCP HTTP/SSE transport for Move37."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.responses import StreamingResponse

from move37.api import __version__ as mcp_version
from move37.api.tool_registry import McpToolRegistry
from move37.services.errors import ServiceError

DEFAULT_PROTOCOL_VERSION = "2024-11-05"
DEFAULT_SERVER_NAME = "move37-api"


class McpSessionManager:
    """Manage SSE sessions and outgoing response queues."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        async with self._lock:
            self._queues[session_id] = asyncio.Queue()
        return session_id

    async def get_queue(self, session_id: str) -> asyncio.Queue | None:
        async with self._lock:
            return self._queues.get(session_id)

    async def remove_session(self, session_id: str) -> None:
        async with self._lock:
            self._queues.pop(session_id, None)


class McpHttpTransport:
    """Handle MCP JSON-RPC over streamable HTTP and SSE."""

    def __init__(self, tool_registry: McpToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._sessions = McpSessionManager()

    async def sse_endpoint(self, request: Request, endpoint_path: str) -> StreamingResponse:
        session_id = await self._sessions.create_session()
        endpoint_url = str(request.base_url).rstrip("/") + endpoint_path + f"?session_id={session_id}"
        return StreamingResponse(
            self._event_stream(session_id, endpoint_url),
            media_type="text/event-stream",
        )

    async def handle_post(self, session_id: str, payload: dict[str, Any], subject: str) -> None:
        queue = await self._sessions.get_queue(session_id)
        if queue is None:
            return
        response = self._handle_json_rpc(payload, subject)
        if response is None:
            return
        await queue.put(response)

    def handle_request(self, payload: dict[str, Any], subject: str) -> dict[str, Any] | None:
        return self._handle_json_rpc(payload, subject)

    async def _event_stream(self, session_id: str, endpoint_url: str):
        queue = await self._sessions.get_queue(session_id)
        if queue is None:
            return
        try:
            yield self._format_event("endpoint", {"endpoint": endpoint_url, "sessionId": session_id})
            while True:
                message = await queue.get()
                yield self._format_event("message", message)
        except asyncio.CancelledError:
            raise
        finally:
            await self._sessions.remove_session(session_id)

    def _handle_json_rpc(self, payload: dict[str, Any], subject: str) -> dict[str, Any] | None:
        method, request_id, params, error = self._parse_json_rpc(payload)
        if error is not None:
            return error
        if request_id is None:
            return None
        try:
            return self._dispatch_method(method, request_id, params, subject)
        except ServiceError as exc:
            return self._error_response(request_id, -32000, exc.message)
        except ValueError as exc:
            return self._error_response(request_id, -32001, str(exc))
        except Exception:
            return self._error_response(request_id, -32603, "Internal error")

    def _parse_json_rpc(
        self,
        payload: dict[str, Any],
    ) -> tuple[str | None, Any, dict[str, Any], dict[str, Any] | None]:
        if not isinstance(payload, dict):
            return None, None, {}, self._error_response(None, -32600, "Invalid Request")
        method = payload.get("method")
        request_id = payload.get("id")
        if payload.get("jsonrpc") != "2.0" or not method:
            return None, request_id, {}, self._error_response(request_id, -32600, "Invalid Request")
        params = payload.get("params", {})
        if params is None:
            params = {}
        return method, request_id, params, None

    def _dispatch_method(
        self,
        method: str,
        request_id: Any,
        params: dict[str, Any],
        subject: str,
    ) -> dict[str, Any]:
        handler = self._method_handlers().get(method)
        if handler is None:
            return self._error_response(request_id, -32601, "Method not found")
        return handler(request_id, params, subject)

    def _method_handlers(self) -> dict[str, Callable[[Any, dict[str, Any], str], dict[str, Any]]]:
        return {
            "initialize": self._handle_initialize,
            "ping": self._handle_ping,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "prompts/list": self._handle_prompts_list,
        }

    def _handle_initialize(self, request_id: Any, params: dict[str, Any], subject: str) -> dict[str, Any]:
        del params, subject
        server_name = os.environ.get("MCP_SERVER_NAME", DEFAULT_SERVER_NAME) or DEFAULT_SERVER_NAME
        server_version = os.environ.get("MCP_SERVER_VERSION", mcp_version) or mcp_version
        return self._result_response(
            request_id,
            {
                "protocolVersion": DEFAULT_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": server_name, "version": server_version},
            },
        )

    def _handle_ping(self, request_id: Any, params: dict[str, Any], subject: str) -> dict[str, Any]:
        del params, subject
        return self._result_response(request_id, {"ok": True})

    def _handle_tools_list(self, request_id: Any, params: dict[str, Any], subject: str) -> dict[str, Any]:
        del params, subject
        return self._result_response(request_id, {"tools": self._tool_registry.list_tools()})

    def _handle_tools_call(self, request_id: Any, params: dict[str, Any], subject: str) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not name:
            return self._error_response(request_id, -32602, "Missing tool name")
        result = self._tool_registry.call_tool(name, arguments, subject)
        return self._result_response(
            request_id,
            {"content": [{"type": "text", "text": json.dumps(result, default=str)}]},
        )

    def _handle_resources_list(
        self,
        request_id: Any,
        params: dict[str, Any],
        subject: str,
    ) -> dict[str, Any]:
        del params, subject
        return self._result_response(request_id, {"resources": []})

    def _handle_prompts_list(
        self,
        request_id: Any,
        params: dict[str, Any],
        subject: str,
    ) -> dict[str, Any]:
        del params, subject
        return self._result_response(request_id, {"prompts": []})

    @staticmethod
    def _result_response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    @staticmethod
    def _format_event(event: str, data: dict[str, Any]) -> str:
        return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
