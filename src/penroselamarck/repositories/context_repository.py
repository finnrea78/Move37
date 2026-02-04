"""
In-memory context repository.

Stores active language context per user.

Public API
----------
- :class:`ContextRepository`: Context get/set operations.

Attributes
----------
DEFAULT_LANGUAGE : str
    Default language when no context is set.

Examples
--------
>>> repo = ContextRepository()
>>> repo.get_context("user")
'da'

See Also
--------
:mod:`penroselamarck.services.context_service`
"""

from __future__ import annotations

from threading import Lock

DEFAULT_LANGUAGE = "da"


class ContextRepository:
    """
    ContextRepository() -> ContextRepository

    Concise (one-line) description of the repository.

    Methods
    -------
    set_context(user_id, language)
        Persist the active language for a user.
    get_context(user_id)
        Retrieve the active language for a user.
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
        self._contexts: dict[str, str] = {}

    def set_context(self, user_id: str, language: str) -> None:
        """
        set_context(user_id, language) -> None

        Concise (one-line) description of the function.

        Parameters
        ----------
        user_id : str
            Identifier for the user.
        language : str
            Language code to set.

        Returns
        -------
        None
            Updates the context mapping.
        """
        with self._lock:
            self._contexts[user_id] = language

    def get_context(self, user_id: str) -> str:
        """
        get_context(user_id) -> str

        Concise (one-line) description of the function.

        Parameters
        ----------
        user_id : str
            Identifier for the user.

        Returns
        -------
        str
            Active language for the user.
        """
        with self._lock:
            return self._contexts.get(user_id, DEFAULT_LANGUAGE)
