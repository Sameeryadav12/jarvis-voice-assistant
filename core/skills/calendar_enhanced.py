"""
Enhanced Calendar Integration Skills

Features:
- Natural language event creation
- Conflict detection
- Recurring rules parser
- Meeting summaries
- Auto-join meetings
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import re
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult
from .calendar import CalendarSkills


@dataclass
class RecurringRule:
    """Represents a recurring event rule."""
    frequency: str  # "daily", "weekly", "monthly", "yearly"
    interval: int = 1  # Every N days/weeks/months
    count: Optional[int] = None  # Number of occurrences
    until: Optional[datetime] = None  # End date
    by_day: List[str] = None  # Days of week (e.g., ["MO", "WE", "FR"])
    
    def to_rrule(self) -> str:
        """Convert to iCalendar RRULE format."""
        # Simplified RRULE format
        freq_map = {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "monthly": "MONTHLY",
            "yearly": "YEARLY",
        }
        
        parts = [f"FREQ={freq_map.get(self.frequency, 'DAILY')}"]
        
        if self.interval > 1:
            parts.append(f"INTERVAL={self.interval}")
        
        if self.count:
            parts.append(f"COUNT={self.count}")
        
        if self.until:
            parts.append(f"UNTIL={self.until.strftime('%Y%m%dT%H%M%S')}")
        
        if self.by_day:
            parts.append(f"BYDAY={','.join(self.by_day)}")
        
        return ";".join(parts)


@dataclass
class EventConflict:
    """Represents a scheduling conflict."""
    conflicting_event_id: str
    conflicting_event_summary: str
    conflicting_event_start: datetime
    conflicting_event_end: datetime


class EnhancedCalendarSkills(CalendarSkills):
    """
    Enhanced calendar skills with natural language processing and advanced features.
    
    Extends base CalendarSkills with:
    - Natural language event creation
    - Conflict detection
    - Recurring rules
    - Meeting summaries
    - Auto-join functionality
    """
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """Initialize enhanced calendar skills."""
        super().__init__(credentials_file)
        self.timezone = "America/Los_Angeles"  # TODO: Make configurable
    
    def parse_natural_language_event(
        self,
        text: str,
        default_start: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Parse natural language event description into structured data.
        
        Examples:
        - "Meeting with John at 3pm tomorrow"
        - "Lunch on Friday at 12:30"
        - "Weekly standup every Monday at 9am"
        - "Dentist appointment next Tuesday at 2pm for 1 hour"
        
        Args:
            text: Natural language event description
            default_start: Default start time if not specified
            
        Returns:
            Dictionary with parsed event data
        """
        if default_start is None:
            default_start = datetime.now()
        
        result = {
            "summary": "",
            "start_time": default_start,
            "end_time": None,
            "duration": timedelta(hours=1),  # Default 1 hour
            "location": "",
            "description": "",
            "recurring": None,
        }
        
        text_lower = text.lower()
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(?:hour|hr|h|minute|min|m)', text_lower)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            if 'hour' in unit or 'hr' in unit or 'h' == unit:
                result["duration"] = timedelta(hours=value)
            elif 'minute' in unit or 'min' in unit or 'm' == unit:
                result["duration"] = timedelta(minutes=value)
        
        # Extract time
        time_patterns = [
            (r'(\d{1,2}):(\d{2})\s*(am|pm)', 'hh:mm am/pm'),
            (r'(\d{1,2})\s*(am|pm)', 'hh am/pm'),
            (r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)?', 'at hh:mm'),
            (r'at\s+(\d{1,2})\s*(am|pm)', 'at hh am/pm'),
        ]
        
        time_str = None
        for pattern, desc in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                hour = int(groups[0])
                
                # Parse minute (if present)
                if desc == 'hh:mm am/pm' or desc == 'at hh:mm':
                    minute = int(groups[1]) if groups[1] and groups[1].isdigit() else 0
                    am_pm = groups[2] if len(groups) > 2 else None
                elif desc == 'hh am/pm' or desc == 'at hh am/pm':
                    minute = 0
                    am_pm = groups[1] if len(groups) > 1 else None
                else:
                    minute = 0
                    am_pm = None
                
                if am_pm:
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                
                result["start_time"] = result["start_time"].replace(hour=hour, minute=minute, second=0, microsecond=0)
                time_str = match.group(0)
                break
        
        # Extract date keywords
        date_keywords = {
            "today": timedelta(days=0),
            "tomorrow": timedelta(days=1),
            "next week": timedelta(days=7),
            "next month": timedelta(days=30),
        }
        
        day_names = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6,
        }
        
        # Check for day names
        for day_name, day_num in day_names.items():
            if day_name in text_lower:
                days_ahead = (day_num - default_start.weekday()) % 7
                if days_ahead == 0 and "next" in text_lower:
                    days_ahead = 7
                result["start_time"] = (default_start + timedelta(days=days_ahead)).replace(
                    hour=result["start_time"].hour,
                    minute=result["start_time"].minute,
                    second=0,
                    microsecond=0,
                )
                break
        
        # Check for date keywords
        for keyword, delta in date_keywords.items():
            if keyword in text_lower:
                result["start_time"] = (default_start + delta).replace(
                    hour=result["start_time"].hour,
                    minute=result["start_time"].minute,
                    second=0,
                    microsecond=0,
                )
                break
        
        # Extract summary (title)
        # Remove time/date keywords to get clean summary
        summary = text
        if time_str:
            summary = summary.replace(time_str, "").strip()
        summary = re.sub(r'\b(at|on|next|tomorrow|today)\b', '', summary, flags=re.IGNORECASE).strip()
        summary = re.sub(r'\b(\d+)\s*(hour|hr|h|minute|min)\b', '', summary, flags=re.IGNORECASE).strip()
        
        # Clean up summary
        summary = re.sub(r'\s+', ' ', summary).strip()
        if summary:
            result["summary"] = summary[:100]  # Limit length
        else:
            result["summary"] = "New Event"
        
        # Extract recurring pattern
        recurring_patterns = {
            r'every\s+day': ("daily", 1),
            r'daily': ("daily", 1),
            r'every\s+week': ("weekly", 1),
            r'weekly': ("weekly", 1),
            r'every\s+month': ("monthly", 1),
            r'monthly': ("monthly", 1),
            r'every\s+(\d+)\s+days?': None,  # Will be handled separately
        }
        
        for pattern, rule_data in recurring_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                if rule_data:
                    frequency, interval = rule_data
                    result["recurring"] = RecurringRule(frequency=frequency, interval=interval)
                else:
                    # Extract interval number
                    interval = int(match.group(1))
                    result["recurring"] = RecurringRule(frequency="daily", interval=interval)
                break
        
        # Set end time
        result["end_time"] = result["start_time"] + result["duration"]
        
        return result
    
    def detect_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary",
    ) -> List[EventConflict]:
        """
        Detect scheduling conflicts for a time range.
        
        Args:
            start_time: Proposed start time
            end_time: Proposed end time
            calendar_id: Calendar to check
            
        Returns:
            List of conflicts
        """
        if not self.service:
            return []
        
        try:
            # Query overlapping events
            time_min = start_time.isoformat()
            time_max = end_time.isoformat()
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            
            conflicts = []
            for event in events_result.get('items', []):
                event_start_str = event['start'].get('dateTime', event['start'].get('date'))
                event_end_str = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse times
                try:
                    event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                    
                    # Check for overlap
                    if (event_start < end_time and event_end > start_time):
                        conflicts.append(EventConflict(
                            conflicting_event_id=event.get('id', ''),
                            conflicting_event_summary=event.get('summary', 'Untitled Event'),
                            conflicting_event_start=event_start,
                            conflicting_event_end=event_end,
                        ))
                except Exception as e:
                    logger.warning(f"Error parsing event time: {e}")
                    continue
            
            return conflicts
        
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []
    
    def create_event_natural_language(
        self,
        text: str,
        check_conflicts: bool = True,
        auto_resolve_conflicts: bool = False,
    ) -> SkillResult:
        """
        Create event from natural language description.
        
        Args:
            text: Natural language event description
            check_conflicts: Whether to check for conflicts
            auto_resolve_conflicts: Automatically find next available time if conflict
            
        Returns:
            Skill result
        """
        if not self.service:
            return SkillResult(
                success=False,
                message="Calendar service not available"
            )
        
        try:
            # Parse natural language
            event_data = self.parse_natural_language_event(text)
            
            # Check conflicts
            conflicts = []
            if check_conflicts:
                conflicts = self.detect_conflicts(
                    event_data["start_time"],
                    event_data["end_time"],
                )
            
            if conflicts and not auto_resolve_conflicts:
                conflict_msg = f"Conflict detected with '{conflicts[0].conflicting_event_summary}'"
                return SkillResult(
                    success=False,
                    message=conflict_msg,
                    data={"conflicts": [c.__dict__ for c in conflicts]}
                )
            
            # Auto-resolve: find next available time
            if conflicts and auto_resolve_conflicts:
                # Try next 30-minute slot
                for i in range(10):  # Try up to 5 hours ahead
                    new_start = event_data["start_time"] + timedelta(minutes=30 * (i + 1))
                    new_end = new_start + event_data["duration"]
                    
                    new_conflicts = self.detect_conflicts(new_start, new_end)
                    if not new_conflicts:
                        event_data["start_time"] = new_start
                        event_data["end_time"] = new_end
                        logger.info(f"Auto-resolved conflict, moved to {new_start}")
                        break
                else:
                    return SkillResult(
                        success=False,
                        message="Could not find available time slot"
                    )
            
            # Build event
            event = {
                'summary': event_data["summary"],
                'location': event_data.get("location", ""),
                'description': event_data.get("description", ""),
                'start': {
                    'dateTime': event_data["start_time"].isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': event_data["end_time"].isoformat(),
                    'timeZone': self.timezone,
                },
            }
            
            # Add recurring rule if specified
            if event_data.get("recurring"):
                event['recurrence'] = ['RRULE:' + event_data["recurring"].to_rrule()]
            
            # Create event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            message = f"Created event '{event_data['summary']}' at {event_data['start_time'].strftime('%I:%M %p on %B %d')}"
            
            return SkillResult(
                success=True,
                message=message,
                data={"event_id": created_event.get('id'), "event": created_event}
            )
        
        except Exception as e:
            logger.error(f"Failed to create event from natural language: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to create event: {str(e)}"
            )
    
    def get_meeting_summary(self, event_id: str) -> SkillResult:
        """
        Get summary for a meeting event.
        
        Args:
            event_id: Event ID
            
        Returns:
            Skill result with meeting summary
        """
        if not self.service:
            return SkillResult(
                success=False,
                message="Calendar service not available"
            )
        
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            summary = {
                "title": event.get('summary', 'Untitled Event'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "location": event.get('location', ''),
                "description": event.get('description', ''),
                "attendees": [a.get('email') for a in event.get('attendees', [])],
                "organizer": event.get('organizer', {}).get('email', ''),
            }
            
            message = f"Meeting: {summary['title']}"
            if summary['location']:
                message += f" at {summary['location']}"
            message += f" from {summary['start']} to {summary['end']}"
            
            return SkillResult(
                success=True,
                message=message,
                data=summary
            )
        
        except Exception as e:
            logger.error(f"Failed to get meeting summary: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to get meeting summary: {str(e)}"
            )
    
    def auto_join_meeting(self, event_id: str) -> SkillResult:
        """
        Auto-join a meeting (opens meeting link).
        
        Args:
            event_id: Event ID
            
        Returns:
            Skill result
        """
        if not self.service:
            return SkillResult(
                success=False,
                message="Calendar service not available"
            )
        
        try:
            import webbrowser
            
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Look for meeting link in description or hangoutLink
            meeting_link = event.get('hangoutLink')
            if not meeting_link:
                # Try to extract from description
                description = event.get('description', '')
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, description)
                if urls:
                    meeting_link = urls[0]
            
            if not meeting_link:
                return SkillResult(
                    success=False,
                    message="No meeting link found for this event"
                )
            
            # Open meeting link
            webbrowser.open(meeting_link)
            
            return SkillResult(
                success=True,
                message=f"Joining meeting: {event.get('summary', 'Untitled')}",
                data={"meeting_link": meeting_link}
            )
        
        except Exception as e:
            logger.error(f"Failed to auto-join meeting: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to join meeting: {str(e)}"
            )
    
    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle enhanced calendar intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        # Delegate to parent for basic intents
        if intent.type == IntentType.CREATE_EVENT:
            # Extract natural language from intent text
            text = intent.text if hasattr(intent, 'text') else ""
            
            if text:
                return self.create_event_natural_language(text, check_conflicts=True)
            else:
                # Fallback to parent implementation
                return super().handle_intent(intent)
        
        return super().handle_intent(intent)

