"""Pydantic schemas shared across services."""

from .bank_account import AccountBalance, Transaction, TransferRequest
from .calendar import CalendarEvent, CalendarEventUpdate
from .github import (
    GitHubIssue,
    GitHubIssueCreate,
    GitHubPullRequest,
    GitHubRepository,
    GitHubWorkflowDispatch,
)

__all__ = [
    "AccountBalance",
    "CalendarEvent",
    "CalendarEventUpdate",
    "GitHubIssue",
    "GitHubIssueCreate",
    "GitHubPullRequest",
    "GitHubRepository",
    "GitHubWorkflowDispatch",
    "Transaction",
    "TransferRequest",
]
