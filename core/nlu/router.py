"""
Command routing from intents to skill execution.
Implements function calling and skill dispatch.
"""

from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
from loguru import logger

from .intents import Intent, IntentType


@dataclass
class SkillResult:
    """
    Result from skill execution.
    
    Attributes:
        success: Whether skill executed successfully
        message: Response message
        data: Optional result data
    """
    success: bool
    message: str
    data: Optional[Any] = None


class CommandRouter:
    """
    Routes classified intents to appropriate skill handlers.
    Implements function calling pattern.
    """

    def __init__(self):
        """Initialize command router."""
        self.handlers: Dict[IntentType, Callable] = {}
        self.middleware: list = []
        logger.info("CommandRouter initialized")

    def register_handler(
        self,
        intent_type: IntentType,
        handler: Callable[[Intent], SkillResult]
    ) -> None:
        """
        Register a handler for an intent type.
        
        Args:
            intent_type: Intent type to handle
            handler: Handler function
        """
        self.handlers[intent_type] = handler
        logger.debug(f"Registered handler for {intent_type.value}")

    def register_middleware(self, middleware: Callable[[Intent], Intent]) -> None:
        """
        Register middleware to process intents before routing.
        
        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)
        logger.debug("Registered middleware")

    async def route(self, intent: Intent) -> SkillResult:
        """
        Route intent to appropriate handler.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill execution result
        """
        # Apply middleware
        for mw in self.middleware:
            try:
                intent = mw(intent)
            except Exception as e:
                logger.error(f"Middleware error: {e}")
        
        # Check for handler
        if intent.type not in self.handlers:
            logger.warning(f"No handler for intent: {intent.type.value}")
            return SkillResult(
                success=False,
                message=f"I don't know how to handle '{intent.raw_text}'"
            )
        
        # Execute handler
        try:
            handler = self.handlers[intent.type]
            logger.debug(f"Routing to handler: {intent.type.value}")
            result = handler(intent)
            return result
        except Exception as e:
            logger.error(f"Handler error: {e}")
            return SkillResult(
                success=False,
                message=f"Error executing command: {str(e)}"
            )

    def get_available_intents(self) -> list:
        """
        Get list of available intent types.
        
        Returns:
            List of registered intent types
        """
        return list(self.handlers.keys())


class SkillRegistry:
    """
    Registry for skill metadata and discovery.
    Supports plugin system for extensibility.
    """

    def __init__(self):
        """Initialize skill registry."""
        self.skills: Dict[str, Dict[str, Any]] = {}
        logger.info("SkillRegistry initialized")

    def register_skill(
        self,
        name: str,
        description: str,
        intents: list,
        handler: Callable,
        permissions: Optional[list] = None
    ) -> None:
        """
        Register a skill with metadata.
        
        Args:
            name: Skill name
            description: Skill description
            intents: List of intent types this skill handles
            handler: Handler function
            permissions: Required permissions (e.g., ['system.volume'])
        """
        self.skills[name] = {
            "description": description,
            "intents": intents,
            "handler": handler,
            "permissions": permissions or [],
            "enabled": True
        }
        logger.info(f"Registered skill: {name}")

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get skill metadata.
        
        Args:
            name: Skill name
            
        Returns:
            Skill metadata or None
        """
        return self.skills.get(name)

    def list_skills(self) -> list:
        """
        List all registered skills.
        
        Returns:
            List of skill names
        """
        return list(self.skills.keys())

    def enable_skill(self, name: str) -> bool:
        """
        Enable a skill.
        
        Args:
            name: Skill name
            
        Returns:
            True if successful
        """
        if name in self.skills:
            self.skills[name]["enabled"] = True
            logger.info(f"Enabled skill: {name}")
            return True
        return False

    def disable_skill(self, name: str) -> bool:
        """
        Disable a skill.
        
        Args:
            name: Skill name
            
        Returns:
            True if successful
        """
        if name in self.skills:
            self.skills[name]["enabled"] = False
            logger.info(f"Disabled skill: {name}")
            return True
        return False





