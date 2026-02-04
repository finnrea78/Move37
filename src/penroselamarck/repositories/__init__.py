"""
Repository layer package.

Provides database access repositories for the Penrose-Lamarck application.

Public API
----------
- :mod:`penroselamarck.repositories.exercise_repository`: Exercise repository.
- :mod:`penroselamarck.repositories.practice_session_repository`: Session repository.
- :mod:`penroselamarck.repositories.attempt_repository`: Attempt repository.
- :mod:`penroselamarck.repositories.performance_repository`: Performance repository.
- :mod:`penroselamarck.repositories.user_repository`: User repository.
- :mod:`penroselamarck.repositories.context_repository`: Context repository.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.repositories.user_repository import UserRepository
>>> isinstance(UserRepository(), UserRepository)
True

See Also
--------
:mod:`penroselamarck.services`
"""
