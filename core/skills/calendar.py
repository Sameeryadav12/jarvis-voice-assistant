"""
Google Calendar integration skills.
Provides event creation, reading, and management.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from loguru import logger

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class CalendarSkills:
    """
    Google Calendar integration skills.
    Requires Google Calendar API credentials.
    """

    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize calendar skills.
        
        Args:
            credentials_file: Path to Google API credentials
        """
        self.credentials_file = credentials_file
        self.service = None
        self._initialize_service()
        logger.info("CalendarSkills initialized")

    def _initialize_service(self) -> None:
        """Initialize Google Calendar API service."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import os.path
            import pickle

            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None

            # Load credentials from token file
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.warning(
                            f"Credentials file not found: {self.credentials_file}. "
                            "Calendar integration will not be available."
                        )
                        return

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar API initialized")

        except ImportError:
            logger.warning(
                "Google Calendar libraries not installed. "
                "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Calendar API: {e}")

    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: str = "",
        location: str = ""
    ) -> SkillResult:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time (defaults to start_time + 1 hour)
            description: Event description
            location: Event location
            
        Returns:
            Skill result
        """
        if not self.service:
            return SkillResult(
                success=False,
                message="Calendar service not available"
            )

        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',  # TODO: Make configurable
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }

        try:
            event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            logger.info(f"Created calendar event: {summary}")
            return SkillResult(
                success=True,
                message=f"Created event '{summary}' at {start_time.strftime('%I:%M %p')}",
                data={"event_id": event.get('id')}
            )
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to create event: {str(e)}"
            )

    def list_upcoming_events(self, max_results: int = 10) -> SkillResult:
        """
        List upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            Skill result with events data
        """
        if not self.service:
            return SkillResult(
                success=False,
                message="Calendar service not available"
            )

        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return SkillResult(
                    success=True,
                    message="No upcoming events found",
                    data={"events": []}
                )

            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_list.append({
                    "summary": event.get('summary', 'No title'),
                    "start": start
                })

            message = f"Found {len(events)} upcoming events"
            logger.info(message)

            return SkillResult(
                success=True,
                message=message,
                data={"events": event_list}
            )
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to list events: {str(e)}"
            )

    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle calendar-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.CREATE_EVENT:
            # Parse event details from entities
            # This is simplified - production would use proper datetime parsing
            summary = "New Event"
            start_time = datetime.now() + timedelta(hours=1)

            # Extract title from entities or raw text
            for entity in intent.entities:
                if entity.type in ["PERSON", "ORG", "EVENT"]:
                    summary = f"Meeting with {entity.value}"

            return self.create_event(summary, start_time)

        return SkillResult(
            success=False,
            message=f"Unknown calendar intent: {intent.type.value}"
        )





