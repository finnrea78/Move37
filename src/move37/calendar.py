"""Compatibility exports for calendar integration types."""

from .schemas.calendar import CalendarEvent, CalendarEventUpdate
from .services.calendar import AppleCalendar, CalendarInterface, GoogleCalendar

__all__ = [
    "AppleCalendar",
    "CalendarEvent",
    "CalendarEventUpdate",
    "CalendarInterface",
    "GoogleCalendar",
]
