"""Move37 service-layer exceptions."""

from __future__ import annotations


class ServiceError(Exception):
    """Base error for service operations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ServiceError):
    """Raised when a requested record does not exist."""


class ConflictError(ServiceError):
    """Raised when a requested mutation violates graph invariants."""


class AuthenticationError(ServiceError):
    """Raised when bearer authentication fails."""
