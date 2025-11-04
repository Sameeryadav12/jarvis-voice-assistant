#!/usr/bin/env python3
"""
Jarvis - Voice-Controlled Desktop Assistant
Main application entry point.
"""

import sys
import argparse
import asyncio
from pathlib import Path
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.audio.capture import AudioCapture
from core.audio.wakeword import WakeWordDetector, WakeWordConfig
from core.nlu.intents import IntentClassifier
from core.nlu.router import CommandRouter, SkillRegistry
from core.skills.system import SystemSkills
from core.skills.calendar import CalendarSkills
from core.skills.reminders import ReminderSkills
from core.memory.vectorstore import VectorMemory
from core.tts.piper import PiperTTS
from core.tts.edge import EdgeTTS


class JarvisAssistant:
    """
    Main Jarvis assistant class.
    Orchestrates all components and manages the conversation loop.
    """

    def __init__(self, config: dict):
        """
        Initialize Jarvis assistant.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.running = False
        
        # Initialize components
        logger.info("Initializing Jarvis...")
        
        # Audio
        self.audio_capture = None
        self.wake_word_detector = None
        
        # NLU
        self.intent_classifier = None
        self.command_router = None
        self.skill_registry = None
        
        # Skills
        self.system_skills = None
        self.calendar_skills = None
        self.reminder_skills = None
        
        # Memory
        self.memory = None
        
        # TTS
        self.tts = None
        
        self._initialize_components()
        
        logger.info("Jarvis initialized successfully")

    def _initialize_components(self) -> None:
        """Initialize all Jarvis components."""
        # Initialize NLU
        self.intent_classifier = IntentClassifier()
        self.command_router = CommandRouter()
        self.skill_registry = SkillRegistry()
        
        # Initialize skills
        self.system_skills = SystemSkills()
        self.information_skills = None
        self.calendar_skills = None
        self.reminder_skills = None
        
        # Always enable information skills
        from core.skills.information import InformationSkills
        self.information_skills = InformationSkills()
        
        if self.config.get('skills', {}).get('calendar', {}).get('enabled'):
            self.calendar_skills = CalendarSkills()
        
        if self.config.get('skills', {}).get('reminders', {}).get('enabled'):
            self.reminder_skills = ReminderSkills()
        
        # Register skill handlers
        from core.nlu.intents import IntentType
        
        # System skills
        system_intents = [
            IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, IntentType.VOLUME_SET,
            IntentType.MUTE, IntentType.UNMUTE,
            IntentType.OPEN_APP, IntentType.CLOSE_APP, IntentType.FOCUS_WINDOW,
            IntentType.MINIMIZE_WINDOW, IntentType.MAXIMIZE_WINDOW
        ]
        for intent_type in system_intents:
            self.command_router.register_handler(intent_type, self.system_skills.handle_intent)
        
        # Information skills
        info_intents = [
            IntentType.GET_TIME, IntentType.GET_DATE, IntentType.GET_SYSTEM_INFO,
            IntentType.GET_BATTERY, IntentType.HELP, IntentType.THANK_YOU,
            IntentType.STOP, IntentType.CANCEL
        ]
        for intent_type in info_intents:
            self.command_router.register_handler(intent_type, self.information_skills.handle_intent)
        
        # Reminder skills
        if self.reminder_skills:
            reminder_intents = [
                IntentType.CREATE_REMINDER, IntentType.SET_TIMER, IntentType.SET_ALARM,
                IntentType.LIST_REMINDERS, IntentType.CANCEL_REMINDER
            ]
            for intent_type in reminder_intents:
                self.command_router.register_handler(intent_type, self.reminder_skills.handle_intent)
        
        # Calendar skills
        if self.calendar_skills:
            calendar_intents = [
                IntentType.CREATE_EVENT, IntentType.LIST_EVENTS, IntentType.CANCEL_EVENT
            ]
            for intent_type in calendar_intents:
                self.command_router.register_handler(intent_type, self.calendar_skills.handle_intent)
        
        # Initialize memory if enabled
        if self.config.get('memory', {}).get('enabled'):
            self.memory = VectorMemory()
        
        # Initialize TTS
        tts_mode = self.config.get('tts', {}).get('mode', 'piper')
        if tts_mode == 'piper':
            self.tts = PiperTTS()
        else:
            self.tts = EdgeTTS()

    def process_command(self, text: str) -> None:
        """
        Process a voice command.
        
        Args:
            text: Transcribed text
        """
        logger.info(f"Processing command: {text}")
        
        # Classify intent
        intent = self.intent_classifier.classify(text)
        logger.debug(f"Intent: {intent.type.value}, confidence: {intent.confidence}")
        
        # Store in memory
        if self.memory:
            self.memory.store(
                text,
                metadata={
                    "type": "user_command",
                    "intent": intent.type.value,
                    "confidence": intent.confidence
                }
            )
        
        # Route to skill
        result = asyncio.run(self.command_router.route(intent))
        
        logger.info(f"Result: {result.message}")
        
        # Speak response
        if self.tts:
            try:
                self.tts.speak(result.message)
            except Exception as e:
                logger.error(f"TTS error: {e}")

    def run_console_mode(self) -> None:
        """Run in console mode (text input for testing)."""
        logger.info("Running in console mode. Type 'quit' to exit.")
        
        while True:
            try:
                text = input("\nYou: ").strip()
                if not text:
                    continue
                
                if text.lower() in ['quit', 'exit', 'bye']:
                    logger.info("Exiting...")
                    break
                
                self.process_command(text)
                
            except KeyboardInterrupt:
                logger.info("\nExiting...")
                break
            except EOFError:
                # Handle end of input gracefully
                logger.info("\nEnd of input. Exiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")

    def run_voice_mode(self) -> None:
        """Run in voice mode (actual voice input)."""
        logger.info("Voice mode not fully implemented yet")
        logger.info("This would start:")
        logger.info("  1. Audio capture")
        logger.info("  2. Wake word detection")
        logger.info("  3. STT processing")
        logger.info("  4. Command execution")
        logger.info("Use console mode for now (--console)")

    def shutdown(self) -> None:
        """Shutdown Jarvis and cleanup resources."""
        logger.info("Shutting down Jarvis...")
        
        if self.reminder_skills:
            self.reminder_skills.shutdown()
        
        logger.info("Goodbye!")


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    import yaml
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Jarvis - Voice-Controlled Desktop Assistant"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Run in console mode (text input for testing)"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Run in voice mode (default)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Configure logger
    logger.remove()
    log_level = "DEBUG" if args.debug else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )
    
    # Load configuration
    config = load_config(args.config)
    
    # Create Jarvis instance
    jarvis = JarvisAssistant(config)
    
    try:
        if args.console:
            jarvis.run_console_mode()
        else:
            jarvis.run_voice_mode()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    finally:
        jarvis.shutdown()


if __name__ == "__main__":
    main()

