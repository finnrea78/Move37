"""
Training REST endpoints.

Defines bulk training import routes.

Public API
----------
- :data:`router`: FastAPI router for training endpoints.

Attributes
----------
router : APIRouter
    Router exposing training endpoints.

Examples
--------
>>> from penroselamarck.mcp.routers.rest.train import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.train_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from penroselamarck.mcp.dependencies import get_service_container
from penroselamarck.mcp.schemas import TrainImportItem, TrainImportOutput
from penroselamarck.services.container import ServiceContainer

router = APIRouter()


@router.post("/train/import", response_model=TrainImportOutput)
def train_import(
    payload: list[TrainImportItem],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> TrainImportOutput:
    """
    train_import(payload, services) -> TrainImportOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    payload : List[TrainImportItem]
        Items to import.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    TrainImportOutput
        Import summary payload.
    """
    result = services.train_service.import_items([item.model_dump() for item in payload])
    return TrainImportOutput(**result)
