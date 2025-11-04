#!/usr/bin/env python3
"""
Quick Demo - Jarvis with Voice Output
Interactive demo showing Jarvis speaking responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from loguru import logger
from core.nlu.router import CommandRouter
from core.skills.system import SystemSkills
from core.skills.information import InformationSkills
from core.skills.reminders import ReminderSkills
from core.tts.edge import EdgeTTS

# tinycolorize is not available, remove it
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")

def main():
    print("\n" + "="*60)
    print("  JARVIS WITH VOICE - INTERACTIVE DEMO")
    print("="*60)
    print("\nJarvis will SPEAK his responses!")
    print("Make sure your speakers are on!\n")
    
    # Initialize TTS
    print("[Initializing Text-to-Speech...]")
    tts = EdgeTTS()
    print("[OK] TTS ready!\n")
    
    # Initialize NLU and Skills
    print("[Initializing Jarvis...]")
    router = CommandRouter()
    
    info_skills = InformationSkills()
    system_skills = SystemSkills()
    reminder_skills = ReminderSkills()
    
    # Register handlers
    router.register_handler("get_time", info_skills.handle_intent)
    router.register_handler("get_date", info_skills.handle_intent)
    router.register_handler("get_battery", info_skills.handle_intent)
    router.register_handler("get_system_info", info_skills.handle_intent)
    router.register_handler("help", info_skills.handle_intent)
    
    router.register_handler("volume_up", system_skills.handle_intent)
    router.register_handler("volume_down", system_skills.handle_intent)
    router.register_handler("volume_set", system_skills.handle_intent)
    router.register_handler("mute", system_skills.handle_intent)
    router.register_handler("unmute", system_skills.handle_intent)
    
    router.register_handler("set_timer", reminder_skills.handle_intent)
    router.register_handler("set_alarm", reminder_skills.handle_intent)
    router.register_handler("create_reminder", reminder_skills.handle_intent)
    
    print("[OK] Jarvis ready!\n")
    
    # Demo commands
    commands = [
        "what time is it",
        "what is the date today",
        "check battery status",
        "help",
    ]
    
    print("Running demo commands...\n")
    
    for i, command in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] You: {command}")
        
        # Get response
        response = router.route(command)
        print(f"Jarvis (text): {response}")
        
        # Speak response
        print("Jarvis (voice): ", end="", flush=True)
        tts.speak(response)
        print("[SPOKE]\n")
    
    # Cleanup
    reminder_skills.shutdown()
    
    print("="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nDid you hear Jarvis speak?")
    print("\nTo use Jarvis interactively:")
    print("  python jarvis_with_voice.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




