"""
Information skills - time, date, weather, system info.
Provides quick information responses.
"""

from datetime import datetime
from typing import Optional
import platform
import psutil
from loguru import logger

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class InformationSkills:
    """
    Information and query skills.
    Provides time, date, weather, system info, etc.
    """

    def __init__(self):
        """Initialize information skills."""
        logger.info("InformationSkills initialized")

    def get_time(self) -> SkillResult:
        """
        Get current time.
        
        Returns:
            Skill result with time
        """
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        
        return SkillResult(
            success=True,
            message=f"The time is {time_str}",
            data={"time": time_str, "datetime": now.isoformat()}
        )

    def get_date(self) -> SkillResult:
        """
        Get current date.
        
        Returns:
            Skill result with date
        """
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        
        return SkillResult(
            success=True,
            message=f"Today is {date_str}",
            data={"date": date_str, "datetime": now.isoformat()}
        )

    def get_system_info(self) -> SkillResult:
        """
        Get system information.
        
        Returns:
            Skill result with system info
        """
        try:
            info = {
                "os": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": psutil.virtual_memory().total // (1024 ** 3),  # GB
                "memory_used": psutil.virtual_memory().used // (1024 ** 3),  # GB
                "memory_percent": psutil.virtual_memory().percent
            }
            
            message = (
                f"Running {info['os']} on {info['processor']}. "
                f"CPU usage: {info['cpu_percent']}%. "
                f"Memory: {info['memory_used']}GB / {info['memory_total']}GB "
                f"({info['memory_percent']}% used)"
            )
            
            return SkillResult(
                success=True,
                message=message,
                data=info
            )
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return SkillResult(
                success=False,
                message="Failed to get system information"
            )

    def get_battery(self) -> SkillResult:
        """
        Get battery status.
        
        Returns:
            Skill result with battery info
        """
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                return SkillResult(
                    success=True,
                    message="No battery detected. This might be a desktop computer."
                )
            
            percent = battery.percent
            plugged = battery.power_plugged
            time_left = battery.secsleft
            
            if plugged:
                message = f"Battery is at {percent}% and charging"
            elif time_left == -1:
                message = f"Battery is at {percent}%"
            else:
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                message = f"Battery is at {percent}% with {hours} hours and {minutes} minutes remaining"
            
            return SkillResult(
                success=True,
                message=message,
                data={
                    "percent": percent,
                    "plugged": plugged,
                    "time_left": time_left
                }
            )
        except Exception as e:
            logger.error(f"Failed to get battery info: {e}")
            return SkillResult(
                success=False,
                message="Failed to get battery information"
            )

    def get_help(self) -> SkillResult:
        """
        Provide help information.
        
        Returns:
            Skill result with help
        """
        help_text = """I can help you with:
        
System Control:
- Turn up/down the volume
- Set volume to a specific level
- Mute or unmute audio

Window Management:
- Open, close, or focus applications
- Minimize or maximize windows

Time & Reminders:
- Set reminders and timers
- Create alarms

Calendar:
- Create and list events
- Schedule meetings

Information:
- Get current time and date
- Check system information
- Check battery status

And more! Just ask naturally."""

        return SkillResult(
            success=True,
            message=help_text,
            data={"help": help_text}
        )

    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle information-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.GET_TIME:
            return self.get_time()
        
        elif intent.type == IntentType.GET_DATE:
            return self.get_date()
        
        elif intent.type == IntentType.GET_SYSTEM_INFO:
            return self.get_system_info()
        
        elif intent.type == IntentType.GET_BATTERY:
            return self.get_battery()
        
        elif intent.type == IntentType.HELP:
            return self.get_help()
        
        elif intent.type == IntentType.THANK_YOU:
            return SkillResult(
                success=True,
                message="You're welcome! Let me know if you need anything else."
            )
        
        elif intent.type == IntentType.STOP or intent.type == IntentType.CANCEL:
            return SkillResult(
                success=True,
                message="Okay, cancelling."
            )
        
        return SkillResult(
            success=False,
            message=f"Unknown information intent: {intent.type.value}"
        )





