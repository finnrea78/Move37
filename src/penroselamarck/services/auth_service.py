"""
Authentication service.

Provides token-based login and demo user retrieval.

Public API
----------
- :class:`AuthService`: Authentication operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.repositories.user_repository import UserRepository
>>> service = AuthService(UserRepository())
>>> isinstance(service.login("token").user_id, str)
True

See Also
--------
:mod:`penroselamarck.repositories.user_repository`
"""

from __future__ import annotations

from penroselamarck.repositories.user_repository import UserRecord, UserRepository


class AuthService:
    """
    AuthService(user_repository) -> AuthService

    Concise (one-line) description of the service.

    Methods
    -------
    login(token)
        Authenticate or create a user for a token.
    demo_user()
        Return the demo user record.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        __init__(user_repository) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        user_repository : UserRepository
            Repository for user storage.

        Returns
        -------
        None
            Initializes the service.
        """
        self._user_repository = user_repository

    def login(self, token: str) -> UserRecord:
        """
        login(token) -> UserRecord

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            Authentication token.

        Returns
        -------
        UserRecord
            Authenticated user record.
        """
        return self._user_repository.get_or_create(token)

    def demo_user(self) -> UserRecord:
        """
        demo_user() -> UserRecord

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        UserRecord
            Demo user record.
        """
        return self._user_repository.get_demo_user()
