"""Pydantic schemas for calendar operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CalendarEvent(BaseModel):
    """Normalized calendar event payload."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    starts_at: datetime
    ends_at: datetime
    description: str | None = None
    location: str | None = None
    attendees: tuple[str, ...] = ()
    metadata: dict[str, str] = Field(default_factory=dict)


class CalendarEventUpdate(BaseModel):
    """Partial update payload for calendar events."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    description: str | None = None
    location: str | None = None
    attendees: tuple[str, ...] | None = None
    metadata: dict[str, str] | None = None
