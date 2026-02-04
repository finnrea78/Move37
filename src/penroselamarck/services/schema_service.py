"""
Database schema service.

Coordinates ORM schema creation for Postgres.

Public API
----------
- :class:`SchemaService`: Schema initialization operations.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.db.session import get_engine
>>> service = SchemaService(get_engine())
>>> callable(service.create_schema)
True

See Also
--------
:mod:`penroselamarck.models.base`
"""

from __future__ import annotations

from sqlalchemy.engine import Engine

from penroselamarck.models.base import Base


class SchemaService:
    """
    SchemaService(engine) -> SchemaService

    Concise (one-line) description of the service.

    Methods
    -------
    create_schema()
        Create all ORM tables if missing.
    """

    def __init__(self, engine: Engine) -> None:
        """
        __init__(engine) -> None

        Concise (one-line) description of the initializer.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine bound to Postgres.

        Returns
        -------
        None
            Initializes the service.
        """
        self._engine = engine

    def create_schema(self) -> None:
        """
        create_schema() -> None

        Concise (one-line) description of the function.

        Parameters
        ----------
        None
            This function does not accept parameters.

        Returns
        -------
        None
            Creates ORM tables if missing.
        """
        Base.metadata.create_all(self._engine)
