"""
Metrics service.

Provides aggregated performance metrics over exercises.

Public API
----------
- :class:`MetricsService`: Metrics operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.db.session import get_engine
>>> from penroselamarck.repositories.performance_repository import PerformanceRepository
>>> service = MetricsService(PerformanceRepository(get_engine()))
>>> callable(service.performance)
True

See Also
--------
:mod:`penroselamarck.repositories.performance_repository`
"""

from __future__ import annotations

from penroselamarck.repositories.performance_repository import PerformanceRepository


class MetricsService:
    """
    MetricsService(performance_repository) -> MetricsService

    Concise (one-line) description of the service.

    Methods
    -------
    performance(language)
        Aggregate performance statistics.
    """

    def __init__(self, performance_repository: PerformanceRepository) -> None:
        """
        __init__(performance_repository) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        performance_repository : PerformanceRepository
            Repository for performance aggregation.

        Returns
        -------
        None
            Initializes the service.
        """
        self._performance_repository = performance_repository

    def performance(self, language: str | None) -> dict:
        """
        performance(language) -> Dict

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : Optional[str]
            Language filter.

        Returns
        -------
        Dict
            Performance statistics and aggregates.
        """
        return self._performance_repository.performance(language)
