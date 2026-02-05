"""
Versioned v1 router assembly.

Aggregates REST and MCP routers under the v1 prefix.

Public API
----------
- :func:`build_v1_router`: Build the v1 router.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.api.routers.v1 import build_v1_router
>>> build_v1_router().prefix
'/v1'

See Also
--------
:mod:`penroselamarck.api.routers.rest`
"""

from __future__ import annotations

from fastapi import APIRouter

from penroselamarck.api.routers.mcp import router as mcp_router
from penroselamarck.api.routers.rest import build_rest_router


def build_v1_router() -> APIRouter:
    """
    build_v1_router() -> APIRouter

    Concise (one-line) description of the function.

    Parameters
    ----------
    None
        This function does not accept parameters.

    Returns
    -------
    APIRouter
        Versioned v1 router.
    """
    router = APIRouter(prefix="/v1")
    router.include_router(build_rest_router())
    router.include_router(mcp_router)
    return router
