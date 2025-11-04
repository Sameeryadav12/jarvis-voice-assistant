#!/usr/bin/env python3
"""
Jarvis - Voice Mode
Full voice-controlled mode with wake word detection and STT.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.audio.audio_pipeline import AudioPipeline, PipelineState
from core.nlu.intents import IntentClassifier
from core.nlu.router import CommandRouter
from core.skills.system import SystemSkills
from core.tts.piper import PiperTTS
from core.tts.edge import EdgeTTS


class JarvisVoice:
    """
    Jarvis voice mode application.
    Handles complete voice interaction loop.
    """

    def __init__(self, config: dict):
        """
        Initialize Jarvis voice mode.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize NLU
        logger.info("Initializing NLU...")
        self.intent_classifier = IntentClassifier()
        self.command_router = CommandRouter()
        
        # Initialize skills
        logger.info("Initializing skills...")
        self.system_skills = SystemSkills()
        
        from core.skills.information import InformationSkills
        from core.skills.reminders import ReminderSkills
        self.information_skills = InformationSkills()
        self.reminder_skills = ReminderSkills() if config.get('skills', {}).get('reminders', {}).get('enabled', True) else None
        
        # Register handlers
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
        
        # Initialize TTS
        logger.info("Initializing TTS...")
        tts_mode = config.get("tts", {}).get("mode", "piper")
        if tts_mode == "piper":
            self.tts = PiperTTS()
        else:
            self.tts = EdgeTTS()
        
        # Initialize audio pipeline
        logger.info("Initializing audio pipeline...")
        self.pipeline = AudioPipeline(
            stt_mode=config.get("stt", {}).get("mode", "offline"),
            wake_word_config=config.get("wake_word", {}),
            stt_config=config.get("stt", {}).get(
                "offline" if config.get("stt", {}).get("mode") == "offline" else "cloud",
                {}
            ),
            on_transcript=self.on_transcript,
            on_state_change=self.on_state_change
        )
        
        logger.info("Jarvis Voice initialized")

    def on_transcript(self, text: str) -> None:
        """
        Handle transcript from STT.
        
        Args:
            text: Transcribed text
        """
        logger.info(f"You said: {text}")
        
        # Classify intent
        intent = self.intent_classifier.classify(text)
        logger.debug(f"Intent: {intent.type.value} (confidence: {intent.confidence})")
        
        # Route to skill
        import asyncio
        result = asyncio.run(self.command_router.route(intent))
        
        logger.info(f"Result: {result.message}")
        
        # Speak response
        try:
            self.tts.speak(result.message)
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def on_state_change(self, state: PipelineState) -> None:
        """
        Handle pipeline state changes.
        
        Args:
            state: New pipeline state
        """
        if state == PipelineState.LISTENING:
            logger.info("👂 Listening for wake word...")
        elif state == PipelineState.WAKE_WORD_DETECTED:
            logger.info("✅ Wake word detected!")
        elif state == PipelineState.PROCESSING_SPEECH:
            logger.info("🗣️ Listening to your command...")
        elif state == PipelineState.ERROR:
            logger.error("❌ Pipeline error")

    def run(self) -> None:
        """Run voice mode."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("  Jarvis Voice Mode - Always Listening")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Say the wake word, then speak your command")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        try:
            # Start pipeline
            self.pipeline.start()
            
            # Keep running
            import time
            while True:
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        finally:
            self.pipeline.stop()
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
        logger.error(f"Config file not found: {config_path}")
        logger.info("Please create config/settings.yaml from settings.example.yaml")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Jarvis - Voice Mode"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to configuration file"
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
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )
    
    # Load configuration
    config = load_config(args.config)
    
    # Validate configuration
    wake_word_key = config.get("wake_word", {}).get("access_key")
    if not wake_word_key:
        logger.error("Picovoice access key not configured!")
        logger.info("Edit config/settings.yaml and add your access key:")
        logger.info("  wake_word:")
        logger.info("    access_key: YOUR_KEY_HERE")
        logger.info("")
        logger.info("Get a free key at: https://console.picovoice.ai")
        sys.exit(1)
    
    stt_mode = config.get("stt", {}).get("mode", "offline")
    if stt_mode == "offline":
        model_path = config.get("stt", {}).get("offline", {}).get("model_path")
        if not Path(model_path).exists():
            logger.warning(f"Whisper model not found: {model_path}")
            logger.info("Download from: https://huggingface.co/ggerganov/whisper.cpp")
            logger.info("Or use cloud mode by changing stt.mode to 'cloud'")
    else:
        api_key = config.get("stt", {}).get("cloud", {}).get("api_key")
        if not api_key:
            logger.error("OpenAI API key not configured for cloud STT!")
            logger.info("Edit config/settings.yaml or use offline mode")
            sys.exit(1)
    
    # Create and run Jarvis
    jarvis = JarvisVoice(config)
    jarvis.run()


if __name__ == "__main__":
    main()

