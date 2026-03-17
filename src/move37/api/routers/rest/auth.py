"""Auth endpoints for the Move37 API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from move37.api.dependencies import get_current_subject
from move37.api.schemas import ViewerOutput

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=ViewerOutput)
def auth_me(subject: Annotated[str, Depends(get_current_subject)]) -> ViewerOutput:
    """Return the authenticated viewer."""

    return ViewerOutput(subject=subject, mode="bearer")
