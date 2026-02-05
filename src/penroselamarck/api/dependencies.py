"""
FastAPI dependency helpers.

Provides access to service container and MCP transport.

Public API
----------
- :func:`get_service_container`: Retrieve the service container.
- :func:`get_mcp_transport`: Retrieve the MCP transport.

Attributes
----------
None

Examples
--------
>>> callable(get_service_container)
True

See Also
--------
:mod:`penroselamarck.services.container`
"""

from __future__ import annotations

from fastapi import Request

from penroselamarck.api.transport import McpHttpTransport
from penroselamarck.services.container import ServiceContainer


def get_service_container(request: Request) -> ServiceContainer:
    """
    get_service_container(request) -> ServiceContainer

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.

    Returns
    -------
    ServiceContainer
        Application service container.
    """
    return request.app.state.services


def get_mcp_transport(request: Request) -> McpHttpTransport:
    """
    get_mcp_transport(request) -> McpHttpTransport

    Concise (one-line) description of the function.

    Parameters
    ----------
    request : Request
        FastAPI request context.

    Returns
    -------
    McpHttpTransport
        MCP transport instance.
    """
    return request.app.state.mcp_transport
