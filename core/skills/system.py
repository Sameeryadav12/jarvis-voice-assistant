"""
System control skills using C++ hooks.
Provides volume control, window management, and system operations.
"""

from typing import Optional
from loguru import logger

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class SystemSkills:
    """
    System control skills.
    Interfaces with C++ native hooks for low-level operations.
    """

    def __init__(self):
        """Initialize system skills."""
        self.native_module = None
        self._load_native_module()
        logger.info("SystemSkills initialized")

    def _load_native_module(self) -> None:
        """Load the C++ native module (jarvis_native) or Python fallback."""
        try:
            # Try C++ module first
            import jarvis_native
            self.native_module = jarvis_native
            logger.info("Loaded jarvis_native C++ module")
        except ImportError:
            # Fall back to Python ctypes implementation
            try:
                from core.bindings import windows_native
                self.native_module = windows_native
                logger.info("Loaded windows_native Python fallback (ctypes)")
            except ImportError as e:
                logger.warning(
                    "Neither jarvis_native C++ module nor windows_native fallback available. "
                    "System control features will not work."
                )

    def set_volume(self, level: float) -> SkillResult:
        """
        Set system master volume.
        
        Args:
            level: Volume level (0.0 to 1.0)
            
        Returns:
            Skill result
        """
        if not self.native_module:
            return SkillResult(
                success=False,
                message="Native audio module not available"
            )
        
        try:
            level = max(0.0, min(1.0, level))  # Clamp to valid range
            self.native_module.set_master_volume(level)
            percentage = int(level * 100)
            logger.info(f"Set volume to {percentage}%")
            return SkillResult(
                success=True,
                message=f"Volume set to {percentage}%",
                data={"volume": level}
            )
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to set volume: {str(e)}"
            )

    def get_volume(self) -> SkillResult:
        """
        Get current system master volume.
        
        Returns:
            Skill result with volume data
        """
        if not self.native_module:
            return SkillResult(
                success=False,
                message="Native audio module not available"
            )
        
        try:
            level = self.native_module.get_master_volume()
            percentage = int(level * 100)
            return SkillResult(
                success=True,
                message=f"Current volume is {percentage}%",
                data={"volume": level}
            )
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to get volume: {str(e)}"
            )

    def volume_up(self, step: float = 0.1) -> SkillResult:
        """
        Increase volume by step.
        
        Args:
            step: Volume increase (default 10%)
            
        Returns:
            Skill result
        """
        current = self.get_volume()
        if not current.success:
            return current
        
        new_level = min(1.0, current.data["volume"] + step)
        return self.set_volume(new_level)

    def volume_down(self, step: float = 0.1) -> SkillResult:
        """
        Decrease volume by step.
        
        Args:
            step: Volume decrease (default 10%)
            
        Returns:
            Skill result
        """
        current = self.get_volume()
        if not current.success:
            return current
        
        new_level = max(0.0, current.data["volume"] - step)
        return self.set_volume(new_level)

    def mute(self) -> SkillResult:
        """
        Mute system audio.
        
        Returns:
            Skill result
        """
        return self.set_volume(0.0)

    def unmute(self) -> SkillResult:
        """
        Unmute system audio (restore to 50% if was 0).
        
        Returns:
            Skill result
        """
        current = self.get_volume()
        if current.success and current.data["volume"] == 0.0:
            return self.set_volume(0.5)
        return SkillResult(success=True, message="Audio already unmuted")

    def focus_window(self, window_title: str) -> SkillResult:
        """
        Focus a window by title.
        
        Args:
            window_title: Window title or partial title
            
        Returns:
            Skill result
        """
        if not self.native_module:
            return SkillResult(
                success=False,
                message="Native window module not available"
            )
        
        try:
            success = self.native_module.focus_window(window_title)
            if success:
                logger.info(f"Focused window: {window_title}")
                return SkillResult(
                    success=True,
                    message=f"Focused window '{window_title}'"
                )
            else:
                return SkillResult(
                    success=False,
                    message=f"Could not find window '{window_title}'"
                )
        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to focus window: {str(e)}"
            )

    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle system-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.VOLUME_UP:
            return self.volume_up()
        
        elif intent.type == IntentType.VOLUME_DOWN:
            return self.volume_down()
        
        elif intent.type == IntentType.VOLUME_SET:
            # Extract volume level from entities
            for entity in intent.entities:
                if entity.type == "volume_level":
                    level = float(entity.value) / 100.0  # Convert percentage
                    return self.set_volume(level)
            return SkillResult(
                success=False,
                message="Please specify a volume level"
            )
        
        elif intent.type == IntentType.MUTE:
            return self.mute()
        
        elif intent.type == IntentType.UNMUTE:
            return self.unmute()
        
        elif intent.type == IntentType.FOCUS_WINDOW:
            # Extract window title from entities
            for entity in intent.entities:
                if entity.type == "app_name":
                    return self.focus_window(entity.value)
            return SkillResult(
                success=False,
                message="Please specify a window name"
            )
        
        return SkillResult(
            success=False,
            message=f"Unknown system intent: {intent.type.value}"
        )


