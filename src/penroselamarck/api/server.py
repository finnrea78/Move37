"""
FastAPI server for MCP and REST endpoints.

Builds the versioned REST and MCP routers with shared services.

Public API
----------
- :func:`create_app`: Builds the FastAPI app.
- :data:`app`: Application instance served by uvicorn.

Attributes
----------
app : FastAPI
    The application instance.

Examples
--------
>>> from penroselamarck.api.server import create_app
>>> app = create_app()
>>> hasattr(app, "router")
True

See Also
--------
:mod:`penroselamarck.api.routers.v1`
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.routing import APIRoute

from penroselamarck.api.routers.oauth import router as oauth_router
from penroselamarck.api.routers.v1 import build_v1_router
from penroselamarck.api.tool_registry import McpToolRegistry
from penroselamarck.api.transport import McpHttpTransport
from penroselamarck.services.container import ServiceContainer


def _generate_unique_id(route: APIRoute) -> str:
    """
    _generate_unique_id(route) -> str

    Concise (one-line) description of the function.

    Parameters
    ----------
    route : APIRoute
        FastAPI route instance.

    Returns
    -------
    str
        Unique operation identifier for the route.
    """
    return f"{route.name}-{route.path_format}".replace("/", "-")


def create_app() -> FastAPI:
    """
    create_app() -> FastAPI

    Concise (one-line) description of the function.

    Parameters
    ----------
    None
        This function does not accept parameters.

    Returns
    -------
    FastAPI
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Penrose-Lamarck MCP (HTTP bridge)",
        version="0.2.0",
        generate_unique_id_function=_generate_unique_id,
    )

    services = ServiceContainer()
    app.state.services = services
    app.state.mcp_transport = McpHttpTransport(McpToolRegistry(services))

    @app.on_event("startup")
    def _startup() -> None:
        """
        _startup() -> None

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        None
            Initializes database schema.
        """
        services.schema_service.create_schema()

    app.include_router(oauth_router)
    app.include_router(build_v1_router())

    return app


app = create_app()
