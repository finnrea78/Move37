"""Pydantic schemas for GitHub operations."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GitHubRepository(BaseModel):
    """Normalized repository payload returned by GitHub clients."""

    model_config = ConfigDict(extra="forbid")

    owner: str
    name: str
    description: str | None = None
    default_branch: str | None = None
    private: bool = False


class GitHubPullRequest(BaseModel):
    """Normalized pull request payload."""

    model_config = ConfigDict(extra="forbid")

    number: int
    title: str
    state: str
    url: str | None = None


class GitHubIssueCreate(BaseModel):
    """Payload used when creating issues through the service layer."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    body: str


class GitHubIssue(BaseModel):
    """Normalized issue payload."""

    model_config = ConfigDict(extra="forbid")

    number: int
    title: str
    state: str
    url: str | None = None


class GitHubWorkflowDispatch(BaseModel):
    """Workflow dispatch request payload."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str
    ref: str
    inputs: dict[str, str] = Field(default_factory=dict)
