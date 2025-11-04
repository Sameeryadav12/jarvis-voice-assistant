"""
Reminder skills using APScheduler.
Provides timer and reminder functionality with desktop notifications.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from loguru import logger

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class ReminderSkills:
    """
    Reminder and timer skills using APScheduler.
    Supports one-time and recurring reminders with notifications.
    """

    def __init__(self, notification_callback: Optional[Callable] = None):
        """
        Initialize reminder skills.
        
        Args:
            notification_callback: Function to call when reminder fires
        """
        self.notification_callback = notification_callback or self._default_notification
        
        # Configure scheduler
        jobstores = {'default': MemoryJobStore()}
        executors = {'default': ThreadPoolExecutor(5)}
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        self.scheduler.start()
        logger.info("ReminderSkills initialized with APScheduler")

    def _default_notification(self, title: str, message: str) -> None:
        """
        Default notification handler.
        
        Args:
            title: Notification title
            message: Notification message
        """
        logger.info(f"REMINDER: {title} - {message}")
        
        try:
            # Try Windows toast notification
            import sys
            if sys.platform == "win32":
                from windows_toasts import Toast, WindowsToaster
                toaster = WindowsToaster("Jarvis")
                toast = Toast()
                toast.text_fields = [title, message]
                toaster.show_toast(toast)
            else:
                # Fallback: just log
                logger.info(f"Notification: {title} - {message}")
        except ImportError:
            logger.warning("windows-toasts not available, using fallback notification")
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

    def create_reminder(
        self,
        message: str,
        when: datetime,
        reminder_id: Optional[str] = None
    ) -> SkillResult:
        """
        Create a one-time reminder.
        
        Args:
            message: Reminder message
            when: When to fire the reminder
            reminder_id: Optional custom reminder ID
            
        Returns:
            Skill result
        """
        if when < datetime.now():
            return SkillResult(
                success=False,
                message="Cannot set reminder in the past"
            )

        try:
            job = self.scheduler.add_job(
                self.notification_callback,
                'date',
                run_date=when,
                args=["Reminder", message],
                id=reminder_id
            )
            
            time_str = when.strftime("%I:%M %p on %B %d")
            logger.info(f"Created reminder '{message}' for {time_str}")
            
            return SkillResult(
                success=True,
                message=f"Reminder set for {time_str}",
                data={"job_id": job.id, "when": when.isoformat()}
            )
        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to create reminder: {str(e)}"
            )

    def create_timer(self, duration_seconds: int, message: str = "Timer") -> SkillResult:
        """
        Create a countdown timer.
        
        Args:
            duration_seconds: Timer duration in seconds
            message: Timer message
            
        Returns:
            Skill result
        """
        when = datetime.now() + timedelta(seconds=duration_seconds)
        return self.create_reminder(message, when)

    def create_recurring_reminder(
        self,
        message: str,
        interval: str,
        **kwargs
    ) -> SkillResult:
        """
        Create a recurring reminder.
        
        Args:
            message: Reminder message
            interval: Interval type ('daily', 'weekly', etc.)
            **kwargs: Additional scheduling parameters
            
        Returns:
            Skill result
        """
        try:
            if interval == "daily":
                trigger = "cron"
                kwargs.setdefault("hour", 9)  # Default to 9 AM
            elif interval == "weekly":
                trigger = "cron"
                kwargs.setdefault("day_of_week", "mon")
                kwargs.setdefault("hour", 9)
            else:
                trigger = "interval"
                kwargs.setdefault("hours", 1)  # Default 1 hour

            job = self.scheduler.add_job(
                self.notification_callback,
                trigger,
                args=["Recurring Reminder", message],
                **kwargs
            )
            
            logger.info(f"Created recurring reminder: {message} ({interval})")
            
            return SkillResult(
                success=True,
                message=f"Recurring reminder set ({interval})",
                data={"job_id": job.id}
            )
        except Exception as e:
            logger.error(f"Failed to create recurring reminder: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to create recurring reminder: {str(e)}"
            )

    def list_reminders(self) -> SkillResult:
        """
        List all active reminders.
        
        Returns:
            Skill result with reminder data
        """
        jobs = self.scheduler.get_jobs()
        
        if not jobs:
            return SkillResult(
                success=True,
                message="No active reminders",
                data={"reminders": []}
            )

        reminders = []
        for job in jobs:
            reminders.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return SkillResult(
            success=True,
            message=f"Found {len(reminders)} active reminders",
            data={"reminders": reminders}
        )

    def cancel_reminder(self, job_id: str) -> SkillResult:
        """
        Cancel a reminder by ID.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            Skill result
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled reminder: {job_id}")
            return SkillResult(
                success=True,
                message=f"Cancelled reminder {job_id}"
            )
        except Exception as e:
            logger.error(f"Failed to cancel reminder: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to cancel reminder: {str(e)}"
            )

    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle reminder-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.CREATE_REMINDER:
            # Parse reminder from intent
            message = "Reminder"
            when = datetime.now() + timedelta(hours=1)

            # Extract time from entities
            time_entity = next((e for e in intent.entities if e.type == "time"), None)
            date_entity = next((e for e in intent.entities if e.type == "date"), None)
            
            if date_entity and isinstance(date_entity.value, datetime):
                when = date_entity.value
                if time_entity and isinstance(time_entity.value, dict):
                    when = when.replace(
                        hour=time_entity.value.get('hour', when.hour),
                        minute=time_entity.value.get('minute', 0)
                    )

            # Extract message from raw text
            text = intent.raw_text.lower()
            for trigger in ["remind me", "reminder", "to"]:
                text = text.replace(trigger, "")
            message = text.strip()

            if not message:
                message = "Reminder"

            return self.create_reminder(message, when)
        
        elif intent.type == IntentType.SET_TIMER:
            # Extract duration from entities
            duration_entity = next((e for e in intent.entities if e.type == "duration"), None)
            
            if duration_entity:
                duration_seconds = duration_entity.value
                message = f"Timer for {duration_seconds} seconds"
            else:
                # Default to 5 minutes
                duration_seconds = 300
                message = "Timer for 5 minutes"
            
            return self.create_timer(duration_seconds, message)
        
        elif intent.type == IntentType.SET_ALARM:
            # Extract time from entities
            time_entity = next((e for e in intent.entities if e.type == "time"), None)
            
            if time_entity and isinstance(time_entity.value, dict):
                now = datetime.now()
                alarm_time = now.replace(
                    hour=time_entity.value.get('hour', now.hour),
                    minute=time_entity.value.get('minute', 0),
                    second=0,
                    microsecond=0
                )
                
                # If time is in the past, set for tomorrow
                if alarm_time < now:
                    alarm_time += timedelta(days=1)
                
                return self.create_reminder("Alarm", alarm_time)
            else:
                return SkillResult(
                    success=False,
                    message="Please specify a time for the alarm"
                )
        
        elif intent.type == IntentType.LIST_REMINDERS:
            return self.list_reminders()
        
        elif intent.type == IntentType.CANCEL_REMINDER:
            # This would need reminder ID extraction
            # For now, just provide guidance
            return SkillResult(
                success=False,
                message="To cancel a reminder, please specify which one"
            )

        return SkillResult(
            success=False,
            message=f"Unknown reminder intent: {intent.type.value}"
        )

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("ReminderSkills scheduler shutdown")

    def __del__(self):
        """Destructor to ensure scheduler shutdown."""
        try:
            self.shutdown()
        except:
            pass

