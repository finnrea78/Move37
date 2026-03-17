"""FastAPI application entrypoint for Move37."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.routing import APIRoute

from move37.api import __version__
from move37.api.tool_registry import McpToolRegistry
from move37.api.transport import McpHttpTransport
from move37.api.routers.v1 import build_v1_router
from move37.services.container import ServiceContainer


def _generate_unique_id(route: APIRoute) -> str:
    """Generate concise route operation ids."""

    return f"{route.name}-{route.path_format}".replace("/", "-")


def create_app() -> FastAPI:
    """Build the FastAPI application."""

    app = FastAPI(
        title=os.environ.get("API_TITLE", "Move37 API"),
        version=os.environ.get("API_VERSION", __version__) or __version__,
        generate_unique_id_function=_generate_unique_id,
    )

    services = ServiceContainer()
    app.state.services = services
    app.state.mcp_transport = McpHttpTransport(McpToolRegistry(services))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(build_v1_router())
    return app


app = create_app()
