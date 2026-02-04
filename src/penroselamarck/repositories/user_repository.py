"""
In-memory user repository.

Stores demo users keyed by token for lightweight authentication flows.

Public API
----------
- :class:`UserRecord`: Lightweight user data container.
- :class:`UserRepository`: User lookup and creation.

Attributes
----------
None

Examples
--------
>>> repo = UserRepository()
>>> isinstance(repo.get_or_create("token").user_id, str)
True

See Also
--------
:mod:`penroselamarck.services.auth_service`
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class UserRecord:
    """
    UserRecord(user_id, roles) -> UserRecord

    Concise (one-line) description of the data structure.

    Parameters
    ----------
    user_id : str
        Unique identifier for the user.
    roles : List[str]
        Role identifiers for authorization.

    Returns
    -------
    UserRecord
        Immutable user record.
    """

    user_id: str
    roles: list[str]


class UserRepository:
    """
    UserRepository() -> UserRepository

    Concise (one-line) description of the repository.

    Methods
    -------
    get_or_create(token)
        Retrieve or create a user for a token.
    get_by_token(token)
        Retrieve a user by token.
    get_demo_user()
        Retrieve or create the demo user.
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
            Initializes repository storage.
        """
        self._lock = Lock()
        self._users_by_token: dict[str, UserRecord] = {}
        self._demo_token = "demo"

    def get_or_create(self, token: str) -> UserRecord:
        """
        get_or_create(token) -> UserRecord

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            Authentication token.

        Returns
        -------
        UserRecord
            Existing or newly created user record.
        """
        with self._lock:
            existing = self._users_by_token.get(token)
            if existing:
                return existing
            record = UserRecord(user_id=str(uuid.uuid4()), roles=["user"])
            self._users_by_token[token] = record
            return record

    def get_by_token(self, token: str) -> UserRecord | None:
        """
        get_by_token(token) -> Optional[UserRecord]

        Concise (one-line) description of the function.

        Parameters
        ----------
        token : str
            Authentication token.

        Returns
        -------
        Optional[UserRecord]
            User record if it exists.
        """
        with self._lock:
            return self._users_by_token.get(token)

    def get_demo_user(self) -> UserRecord:
        """
        get_demo_user() -> UserRecord

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
        return self.get_or_create(self._demo_token)
