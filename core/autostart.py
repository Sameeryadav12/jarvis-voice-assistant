"""
Autostart Management for Jarvis

Features:
- Windows startup integration
- Registry-based autostart
- Enable/disable autostart
- Check autostart status
"""

import sys
import os
import winreg
from pathlib import Path
from typing import Optional
from loguru import logger


class AutostartManager:
    """
    Manages Windows autostart functionality.
    
    Uses Windows Registry to add/remove Jarvis from startup programs.
    """
    
    # Registry key for autostart
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "JarvisAssistant"
    
    def __init__(self, executable_path: Optional[Path] = None):
        """
        Initialize autostart manager.
        
        Args:
            executable_path: Path to Jarvis executable (auto-detected if None)
        """
        if executable_path is None:
            executable_path = self._get_executable_path()
        
        self.executable_path = executable_path
        logger.info(f"AutostartManager initialized with: {self.executable_path}")
    
    def _get_executable_path(self) -> Path:
        """
        Get path to current executable.
        
        Returns:
            Path to executable
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys.executable)
        else:
            # Running as script
            script_path = Path(__file__).parent.parent / "jarvis_ui.py"
            return Path(sys.executable).parent / "pythonw.exe"
    
    def is_enabled(self) -> bool:
        """
        Check if autostart is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return value is not None and len(value) > 0
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        
        except Exception as e:
            logger.error(f"Failed to check autostart status: {e}")
            return False
    
    def enable(self, minimized: bool = True) -> bool:
        """
        Enable autostart.
        
        Args:
            minimized: Start minimized to system tray
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Build command
            command = f'"{self.executable_path}"'
            if minimized:
                command += " --minimized"
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            # Set value
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                command
            )
            
            winreg.CloseKey(key)
            
            logger.info(f"Autostart enabled: {command}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable(self) -> bool:
        """
        Disable autostart.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            try:
                winreg.DeleteValue(key, self.APP_NAME)
                logger.info("Autostart disabled")
                success = True
            except FileNotFoundError:
                # Already disabled
                success = True
            finally:
                winreg.CloseKey(key)
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to disable autostart: {e}")
            return False
    
    def toggle(self) -> bool:
        """
        Toggle autostart on/off.
        
        Returns:
            New state (True if enabled, False if disabled)
        """
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True
    
    def get_command(self) -> Optional[str]:
        """
        Get current autostart command.
        
        Returns:
            Command string or None if not enabled
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                return value
            except FileNotFoundError:
                return None
            finally:
                winreg.CloseKey(key)
        
        except Exception as e:
            logger.error(f"Failed to get autostart command: {e}")
            return None


# Singleton instance
_autostart_manager: Optional[AutostartManager] = None


def get_autostart_manager() -> AutostartManager:
    """
    Get singleton autostart manager instance.
    
    Returns:
        AutostartManager instance
    """
    global _autostart_manager
    if _autostart_manager is None:
        _autostart_manager = AutostartManager()
    return _autostart_manager


if __name__ == "__main__":
    # CLI interface
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Jarvis autostart")
    parser.add_argument("action", choices=["enable", "disable", "toggle", "status"], help="Action to perform")
    
    args = parser.parse_args()
    
    manager = get_autostart_manager()
    
    if args.action == "enable":
        success = manager.enable()
        print(f"Autostart {'enabled' if success else 'failed'}")
    elif args.action == "disable":
        success = manager.disable()
        print(f"Autostart {'disabled' if success else 'failed'}")
    elif args.action == "toggle":
        new_state = manager.toggle()
        print(f"Autostart {'enabled' if new_state else 'disabled'}")
    elif args.action == "status":
        enabled = manager.is_enabled()
        print(f"Autostart is {'enabled' if enabled else 'disabled'}")
        if enabled:
            print(f"Command: {manager.get_command()}")

