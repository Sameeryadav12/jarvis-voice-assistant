#!/usr/bin/env python3
"""
Jarvis with Voice Output
Console mode with text-to-speech responses!
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
from core.tts.edge import EdgeTTS
import asyncio


def main():
    """Console mode with voice output."""
    print("\n" + "=" * 60)
    print("  JARVIS - Voice Assistant (With Speech Output!)")
    print("=" * 60)
    print("\nInitializing...")
    
    # Suppress debug logs
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    # Initialize components
    classifier = IntentClassifier()
    router = CommandRouter()
    info_skills = InformationSkills()
    system_skills = SystemSkills()
    reminder_skills = ReminderSkills()
    tts = EdgeTTS(voice="en-US-AriaNeural")
    
    # Register all handlers
    info_intents = [
        IntentType.GET_TIME, IntentType.GET_DATE, IntentType.GET_SYSTEM_INFO,
        IntentType.GET_BATTERY, IntentType.HELP, IntentType.THANK_YOU,
        IntentType.STOP, IntentType.CANCEL
    ]
    for intent_type in info_intents:
        router.register_handler(intent_type, info_skills.handle_intent)
    
    system_intents = [
        IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, IntentType.VOLUME_SET,
        IntentType.MUTE, IntentType.UNMUTE, IntentType.FOCUS_WINDOW
    ]
    for intent_type in system_intents:
        router.register_handler(intent_type, system_skills.handle_intent)
    
    reminder_intents = [
        IntentType.SET_TIMER, IntentType.SET_ALARM, IntentType.CREATE_REMINDER,
        IntentType.LIST_REMINDERS
    ]
    for intent_type in reminder_intents:
        router.register_handler(intent_type, reminder_skills.handle_intent)
    
    print("\n[OK] Jarvis initialized with voice output!")
    print("\nType commands and Jarvis will respond with VOICE!")
    print("Type 'help' to see available commands")
    print("Type 'quit' to exit")
    print("Type 'mute tts' to disable voice (text only)")
    print("=" * 60)
    
    voice_enabled = True
    
    # Main loop
    while True:
        try:
            # Get input
            text = input("\nYou: ").strip()
            
            if not text:
                continue
            
            # Check for special commands
            if text.lower() == 'mute tts':
                voice_enabled = False
                print("Jarvis: [Voice output disabled]")
                continue
            
            if text.lower() == 'unmute tts':
                voice_enabled = True
                print("Jarvis: [Voice output enabled]")
                tts.speak("Voice output enabled")
                continue
            
            # Check for exit
            if text.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                goodbye_msg = "Goodbye! Have a great day!"
                print(f"\nJarvis: {goodbye_msg}")
                if voice_enabled:
                    tts.speak(goodbye_msg)
                break
            
            # Process command
            intent = classifier.classify(text)
            result = asyncio.run(router.route(intent))
            
            # Show and speak result
            print(f"Jarvis: {result.message}")
            
            if voice_enabled and result.success:
                try:
                    # Speak response (don't block on playback)
                    asyncio.run(tts.speak_async(result.message, play_audio=True))
                except Exception as e:
                    print(f"  [TTS Error: {e}]")
            
        except KeyboardInterrupt:
            print("\n\nJarvis: Goodbye!")
            if voice_enabled:
                tts.speak("Goodbye")
            break
        except EOFError:
            print("\n\nJarvis: End of input. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'help'")
    
    # Cleanup
    reminder_skills.shutdown()


if __name__ == "__main__":
    main()




