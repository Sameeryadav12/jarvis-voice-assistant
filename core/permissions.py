"""
Permissions and security system.

Implements scoped permissions for skills to ensure privacy and security.
"""

from enum import Enum
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from loguru import logger
import json
from pathlib import Path


class PermissionScope(Enum):
    """Permission scopes for skills."""
    
    # System-level permissions
    SYSTEM_CONTROL = "system_control"      # Volume, brightness, shutdown
    WINDOW_MANAGEMENT = "window_management"  # Focus, close windows
    FILE_SYSTEM = "filesystem"              # Read/write files
    NETWORK = "network"                     # Web access, API calls
    CLIPBOARD = "clipboard"                 # Read/write clipboard
    NOTIFICATIONS = "notifications"         # Send notifications
    
    # Sensitive permissions
    PERSONAL_DATA = "personal_data"         # Access user data
    CALENDAR = "calendar"                   # Calendar access
    CONTACTS = "contacts"                   # Contact access
    LOCATION = "location"                   # Location access
    
    # Audio/Video permissions
    AUDIO_CAPTURE = "audio_capture"        # Microphone access
    SCREEN_CAPTURE = "screen_capture"      # Screenshot, recording


@dataclass
class PermissionConfig:
    """
    Permission configuration for a skill.
    
    Attributes:
        skill_name: Name of the skill
        required_scopes: Set of required permission scopes
        granted: Whether permissions are granted
        last_asked: Timestamp of last permission request
        auto_grant: Whether to auto-grant for trusted skills
    """
    skill_name: str
    required_scopes: Set[PermissionScope] = field(default_factory=set)
    granted: bool = False
    last_asked: Optional[float] = None
    auto_grant: bool = False


class PermissionManager:
    """
    Manages permissions for all skills.
    
    Features:
    - Per-skill permission scopes
    - Permission prompts for user consent
    - Persistent permission storage
    - Auto-grant for trusted skills
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize permission manager.
        
        Args:
            config_path: Path to permission configuration file
        """
        if config_path is None:
            config_path = Path.home() / ".jarvis" / "permissions.json"
        
        self.config_path = config_path
        self.permissions: Dict[str, PermissionConfig] = {}
        self.trusted_skills: Set[str] = {"InformationSkills"}  # Core skills are trusted
        
        # Load existing permissions
        self._load_permissions()
        
        logger.info("PermissionManager initialized")
    
    def _load_permissions(self):
        """Load permissions from disk."""
        if not self.config_path.exists():
            logger.debug(f"Permissions file not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            for skill_name, config_data in data.items():
                scopes = {PermissionScope(s) for s in config_data.get('required_scopes', [])}
                self.permissions[skill_name] = PermissionConfig(
                    skill_name=skill_name,
                    required_scopes=scopes,
                    granted=config_data.get('granted', False),
                    last_asked=config_data.get('last_asked'),
                    auto_grant=config_data.get('auto_grant', False)
                )
            
            logger.info(f"Loaded permissions for {len(self.permissions)} skills")
        
        except Exception as e:
            logger.error(f"Failed to load permissions: {e}")
    
    def _save_permissions(self):
        """Save permissions to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for skill_name, config in self.permissions.items():
                data[skill_name] = {
                    'required_scopes': [s.value for s in config.required_scopes],
                    'granted': config.granted,
                    'last_asked': config.last_asked,
                    'auto_grant': config.auto_grant
                }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Permissions saved successfully")
        
        except Exception as e:
            logger.error(f"Failed to save permissions: {e}")
    
    def register_skill(
        self,
        skill_name: str,
        required_scopes: Set[PermissionScope],
        auto_grant: bool = False
    ):
        """
        Register a skill with its required permissions.
        
        Args:
            skill_name: Name of the skill
            required_scopes: Set of required permission scopes
            auto_grant: Whether to auto-grant permissions
        """
        self.permissions[skill_name] = PermissionConfig(
            skill_name=skill_name,
            required_scopes=required_scopes,
            granted=auto_grant or skill_name in self.trusted_skills,
            auto_grant=auto_grant
        )
        
        logger.debug(f"Registered skill: {skill_name} with scopes: {required_scopes}")
        self._save_permissions()
    
    def check_permission(self, skill_name: str, scope: PermissionScope) -> bool:
        """
        Check if a skill has a specific permission.
        
        Args:
            skill_name: Name of the skill
            scope: Permission scope to check
            
        Returns:
            True if permission is granted, False otherwise
        """
        config = self.permissions.get(skill_name)
        
        if not config:
            logger.warning(f"Skill not registered: {skill_name}")
            return False
        
        if scope not in config.required_scopes:
            logger.warning(f"Skill {skill_name} doesn't require {scope}")
            return True
        
        return config.granted
    
    def request_permission(self, skill_name: str, scope: PermissionScope) -> bool:
        """
        Request permission for a skill (prompt user).
        
        Args:
            skill_name: Name of the skill
            scope: Permission scope to request
            
        Returns:
            True if permission granted, False otherwise
        """
        config = self.permissions.get(skill_name)
        
        if not config:
            logger.warning(f"Skill not registered: {skill_name}")
            return False
        
        # Already granted
        if config.granted:
            return True
        
        # Trusted skills auto-grant
        if skill_name in self.trusted_skills or config.auto_grant:
            config.granted = True
            self._save_permissions()
            return True
        
        # Prompt user (in interactive mode)
        # TODO: Implement actual UI prompt
        logger.info(f"Permission requested: {skill_name} needs {scope}")
        
        # For now, return False (needs user approval)
        return False
    
    def grant_permission(self, skill_name: str):
        """
        Grant permissions to a skill.
        
        Args:
            skill_name: Name of the skill
        """
        config = self.permissions.get(skill_name)
        if config:
            config.granted = True
            self._save_permissions()
            logger.info(f"Permissions granted to: {skill_name}")
    
    def revoke_permission(self, skill_name: str):
        """
        Revoke permissions from a skill.
        
        Args:
            skill_name: Name of the skill
        """
        config = self.permissions.get(skill_name)
        if config:
            config.granted = False
            self._save_permissions()
            logger.info(f"Permissions revoked from: {skill_name}")


# Global permission manager instance
_permission_manager: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    """Get the global permission manager instance."""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


def check_skill_permission(skill_name: str, scope: PermissionScope) -> bool:
    """
    Check if a skill has a specific permission.
    
    Args:
        skill_name: Name of the skill
        scope: Permission scope to check
        
    Returns:
        True if permission granted
    """
    return get_permission_manager().check_permission(skill_name, scope)


def require_permission(scope: PermissionScope):
    """
    Decorator to require a permission scope for a skill method.
    
    Usage:
        @require_permission(PermissionScope.NETWORK)
        def my_skill_method(self):
            pass
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            skill_name = self.__class__.__name__
            if not check_skill_permission(skill_name, scope):
                logger.warning(
                    f"Permission denied: {skill_name} requires {scope}"
                )
                return {
                    'success': False,
                    'message': f'Permission denied: {scope.value} required'
                }
            return func(self, *args, **kwargs)
        return wrapper
    return decorator



