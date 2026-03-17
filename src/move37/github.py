"""Compatibility exports for GitHub integration types."""

from .schemas.github import (
    GitHubIssue,
    GitHubIssueCreate,
    GitHubPullRequest,
    GitHubRepository,
    GitHubWorkflowDispatch,
)
from .services.github import GitHubInterface

__all__ = [
    "GitHubInterface",
    "GitHubIssue",
    "GitHubIssueCreate",
    "GitHubPullRequest",
    "GitHubRepository",
    "GitHubWorkflowDispatch",
]
