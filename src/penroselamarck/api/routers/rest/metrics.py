"""
Metrics REST endpoints.

Defines routes for performance metrics.

Public API
----------
- :data:`router`: FastAPI router for metrics endpoints.

Attributes
----------
router : APIRouter
    Router exposing metrics endpoints.

Examples
--------
>>> from penroselamarck.api.routers.rest.metrics import router
>>> router.prefix
''

See Also
--------
:mod:`penroselamarck.services.metrics_service`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from penroselamarck.api.dependencies import get_service_container
from penroselamarck.api.schemas import PerformanceOutput, PerformanceQuery
from penroselamarck.schemas.performance_summary import PerformanceSummary
from penroselamarck.services.container import ServiceContainer

router = APIRouter()


@router.get("/metrics/performance", response_model=PerformanceOutput)
def metrics_performance(
    q: Annotated[PerformanceQuery, Depends()],
    services: Annotated[ServiceContainer, Depends(get_service_container)],
) -> PerformanceOutput:
    """
    metrics_performance(q, services) -> PerformanceOutput

    Concise (one-line) description of the function.

    Parameters
    ----------
    q : PerformanceQuery
        Query filters for metrics.
    services : ServiceContainer
        Service container dependency.

    Returns
    -------
    PerformanceOutput
        Performance metrics payload.
    """
    data = services.metrics_service.performance(q.language)
    items = [PerformanceSummary(**item) for item in data["items"]]
    return PerformanceOutput(items=items, aggregates=data["aggregates"])
