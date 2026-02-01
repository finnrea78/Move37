"""
SQLAlchemy Base declarative.

Short summary describing the module's purpose.

Optional longer description with context, constraints, and side effects.

Public API
----------
- :class:`Base`: Declarative base for ORM models.

Examples
--------
>>> from penroselamarck.models.base import Base
>>> hasattr(Base, 'metadata')
True
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base() -> Declarative Base class

    Concise (one-line) description of the class.

    Returns
    -------
    DeclarativeBase subclass
        Declarative base used by all ORM models.
    """

    pass
