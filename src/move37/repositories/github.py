"""Repository for GitHub integration records."""

from __future__ import annotations

from sqlalchemy.orm import Session

from move37.models.integrations import GitHubIntegrationModel


class GitHubIntegrationRepository:
    """SQLAlchemy repository for GitHub integration metadata."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_login(self, login: str) -> GitHubIntegrationModel | None:
        return (
            self._session.query(GitHubIntegrationModel)
            .filter(GitHubIntegrationModel.login == login)
            .one_or_none()
        )

    def save(self, integration: GitHubIntegrationModel) -> GitHubIntegrationModel:
        self._session.add(integration)
        self._session.flush()
        return integration
