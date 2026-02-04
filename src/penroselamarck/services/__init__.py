"""
Service layer package.

Provides business logic services for the Penrose-Lamarck application.

Public API
----------
- :mod:`penroselamarck.services.container`: Service container wiring.
- :mod:`penroselamarck.services.auth_service`: Authentication service.
- :mod:`penroselamarck.services.context_service`: Context service.
- :mod:`penroselamarck.services.exercise_service`: Exercise service.
- :mod:`penroselamarck.services.train_service`: Training import service.
- :mod:`penroselamarck.services.practice_service`: Practice service.
- :mod:`penroselamarck.services.metrics_service`: Metrics service.
- :mod:`penroselamarck.services.schema_service`: Schema service.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.services.container import ServiceContainer
>>> isinstance(ServiceContainer(), ServiceContainer)
True

See Also
--------
:mod:`penroselamarck.repositories`
"""
