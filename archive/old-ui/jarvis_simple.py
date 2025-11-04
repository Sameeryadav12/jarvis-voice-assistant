#!/usr/bin/env python3
"""
Jarvis Simple Console Mode
A streamlined, working version for testing.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Check if stdin is interactive
IS_INTERACTIVE = sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else True

sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
from core.wizard import should_run_wizard, run_first_run_wizard
import asyncio


def main():
    """Simple console mode."""
    # Check for first run
    if should_run_wizard():
        run_first_run_wizard()
        print("\nContinuing to main interface...\n")
    
    print("\n" + "=" * 60)
    print("  JARVIS - Voice Assistant (Console Mode)")
    print("=" * 60)
    print("\nInitializing...")
    
    # Initialize components (quietly)
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    classifier = IntentClassifier()
    router = CommandRouter()
    info_skills = InformationSkills()
    system_skills = SystemSkills()
    reminder_skills = ReminderSkills()
    
    # Register handlers
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
    
    # Register reminder handlers (ADDED!)
    reminder_intents = [
        IntentType.SET_TIMER, IntentType.SET_ALARM, IntentType.CREATE_REMINDER,
        IntentType.LIST_REMINDERS
    ]
    for intent_type in reminder_intents:
        router.register_handler(intent_type, reminder_skills.handle_intent)
    
    print("\n[OK] Jarvis initialized successfully!")
    print("\nType 'help' to see available commands")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    # Main loop
    while True:
        try:
            # Get input - only prompt if interactive
            if IS_INTERACTIVE:
                text = input("\nYou: ").strip()
            else:
                # In non-interactive mode, read entire line
                try:
                    text = input().strip()
                except:
                    text = ""
            
            if not text:
                continue
            
            # Check for exit
            if text.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\nJarvis: Goodbye! Have a great day!")
                break
            
            # Process command
            intent = classifier.classify(text)
            result = asyncio.run(router.route(intent))
            
            # Show result
            print(f"Jarvis: {result.message}")
            
        except KeyboardInterrupt:
            print("\nJarvis: Goodbye!")
            break
        except EOFError:
            if IS_INTERACTIVE:
                print("\n\nJarvis: End of input. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'help'")
    
    # Cleanup
    if 'reminder_skills' in locals():
        reminder_skills.shutdown()


if __name__ == "__main__":
    main()

