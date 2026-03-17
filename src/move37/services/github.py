"""Service interfaces for GitHub integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from move37.schemas.github import (
    GitHubIssue,
    GitHubIssueCreate,
    GitHubPullRequest,
    GitHubRepository,
    GitHubWorkflowDispatch,
)


class GitHubInterface(ABC):
    """Contract for service-layer GitHub operations."""

    @abstractmethod
    def get_repository(self, owner: str, repo: str) -> GitHubRepository:
        """Return normalized repository metadata."""

    @abstractmethod
    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
    ) -> Sequence[GitHubPullRequest]:
        """Return pull requests for a repository."""

    @abstractmethod
    def create_issue(
        self,
        owner: str,
        repo: str,
        issue: GitHubIssueCreate,
    ) -> GitHubIssue:
        """Create an issue and return the normalized result."""

    @abstractmethod
    def trigger_workflow(
        self,
        owner: str,
        repo: str,
        dispatch: GitHubWorkflowDispatch,
    ) -> None:
        """Dispatch a GitHub Actions workflow."""
