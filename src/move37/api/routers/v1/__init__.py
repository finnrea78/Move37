"""Versioned router assembly for Move37."""

from __future__ import annotations

from fastapi import APIRouter

from move37.api.routers.mcp import router as mcp_router
from move37.api.routers.rest import build_rest_router


def build_v1_router() -> APIRouter:
    """Return the versioned v1 router."""

    router = APIRouter(prefix="/v1")
    router.include_router(build_rest_router())
    router.include_router(mcp_router)
    return router
