"""Repository for calendar connection records."""

from __future__ import annotations

from sqlalchemy.orm import Session

from move37.models.integrations import CalendarConnectionModel


class CalendarConnectionRepository:
    """SQLAlchemy repository for calendar provider connections."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_provider_calendar(
        self,
        provider: str,
        external_calendar_id: str,
    ) -> CalendarConnectionModel | None:
        return (
            self._session.query(CalendarConnectionModel)
            .filter(CalendarConnectionModel.provider == provider)
            .filter(CalendarConnectionModel.external_calendar_id == external_calendar_id)
            .one_or_none()
        )

    def save(
        self,
        connection: CalendarConnectionModel,
    ) -> CalendarConnectionModel:
        self._session.add(connection)
        self._session.flush()
        return connection
