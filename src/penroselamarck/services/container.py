"""
Service container wiring.

Builds repositories and services for dependency injection.

Public API
----------
- :class:`ServiceContainer`: Dependency container for services.

Attributes
----------
None

Examples
--------
>>> container = ServiceContainer()
>>> hasattr(container, "exercise_service")
True

See Also
--------
:mod:`penroselamarck.services`
"""

from __future__ import annotations

from penroselamarck.db.session import get_engine
from penroselamarck.repositories.attempt_repository import AttemptRepository
from penroselamarck.repositories.context_repository import ContextRepository
from penroselamarck.repositories.exercise_repository import ExerciseRepository
from penroselamarck.repositories.performance_repository import PerformanceRepository
from penroselamarck.repositories.practice_session_repository import PracticeSessionRepository
from penroselamarck.repositories.user_repository import UserRepository
from penroselamarck.services.auth_service import AuthService
from penroselamarck.services.context_service import ContextService
from penroselamarck.services.exercise_service import ExerciseService
from penroselamarck.services.metrics_service import MetricsService
from penroselamarck.services.practice_service import PracticeService
from penroselamarck.services.schema_service import SchemaService
from penroselamarck.services.train_service import TrainService


class ServiceContainer:
    """
    ServiceContainer() -> ServiceContainer

    Concise (one-line) description of the container.

    Attributes
    ----------
    engine : Engine
        SQLAlchemy engine for database access.
    auth_service : AuthService
        Authentication service.
    context_service : ContextService
        Context service.
    exercise_service : ExerciseService
        Exercise service.
    train_service : TrainService
        Training import service.
    practice_service : PracticeService
        Practice service.
    metrics_service : MetricsService
        Metrics service.
    schema_service : SchemaService
        Database schema service.
    """

    def __init__(self) -> None:
        """
        __init__() -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        None
            This initializer does not accept parameters.

        Returns
        -------
        None
            Initializes repositories and services.
        """
        self.engine = get_engine()

        user_repository = UserRepository()
        context_repository = ContextRepository()
        exercise_repository = ExerciseRepository(self.engine)
        session_repository = PracticeSessionRepository(self.engine)
        attempt_repository = AttemptRepository(self.engine)
        performance_repository = PerformanceRepository(self.engine)

        self.auth_service = AuthService(user_repository)
        self.context_service = ContextService(context_repository, user_repository)
        self.exercise_service = ExerciseService(exercise_repository)
        self.train_service = TrainService(self.exercise_service)
        self.practice_service = PracticeService(
            exercise_repository,
            session_repository,
            attempt_repository,
        )
        self.metrics_service = MetricsService(performance_repository)
        self.schema_service = SchemaService(self.engine)
