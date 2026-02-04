"""
Study context service.

Manages active language context for a user.

Public API
----------
- :class:`ContextService`: Context operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.repositories.context_repository import ContextRepository
>>> from penroselamarck.repositories.user_repository import UserRepository
>>> service = ContextService(ContextRepository(), UserRepository())
>>> isinstance(service.get_context().language, str)
True

See Also
--------
:mod:`penroselamarck.repositories.context_repository`
"""

from __future__ import annotations

from dataclasses import dataclass

from penroselamarck.repositories.context_repository import ContextRepository
from penroselamarck.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class ContextState:
    """
    ContextState(active_context_id, language) -> ContextState

    Concise (one-line) description of the data structure.

    Parameters
    ----------
    active_context_id : str
        Identifier for the active context.
    language : str
        Language associated with the context.

    Returns
    -------
    ContextState
        Immutable context state.
    """

    active_context_id: str
    language: str


class ContextService:
    """
    ContextService(context_repository, user_repository) -> ContextService

    Concise (one-line) description of the service.

    Methods
    -------
    set_context(language)
        Update the demo user's context.
    get_context()
        Retrieve the demo user's context.
    """

    def __init__(
        self, context_repository: ContextRepository, user_repository: UserRepository
    ) -> None:
        """
        __init__(context_repository, user_repository) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        context_repository : ContextRepository
            Repository for context storage.
        user_repository : UserRepository
            Repository for user storage.

        Returns
        -------
        None
            Initializes the service.
        """
        self._context_repository = context_repository
        self._user_repository = user_repository

    def set_context(self, language: str) -> ContextState:
        """
        set_context(language) -> ContextState

        Concise (one-line) description of the function.

        Parameters
        ----------
        language : str
            Language code to set.

        Returns
        -------
        ContextState
            Updated context state.
        """
        user = self._user_repository.get_demo_user()
        self._context_repository.set_context(user.user_id, language)
        return ContextState(active_context_id=user.user_id, language=language)

    def get_context(self) -> ContextState:
        """
        get_context() -> ContextState

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        ContextState
            Current context state.
        """
        user = self._user_repository.get_demo_user()
        language = self._context_repository.get_context(user.user_id)
        return ContextState(active_context_id=user.user_id, language=language)
