"""
Skills module for Jarvis.
Contains all executable skills (system, calendar, reminders, web, etc.).
"""

from .system import SystemSkills
from .calendar import CalendarSkills
from .reminders import ReminderSkills
from .web import WebSkills
from .information import InformationSkills

__all__ = [
    "SystemSkills",
    "CalendarSkills",
    "ReminderSkills",
    "WebSkills",
    "InformationSkills"
]

