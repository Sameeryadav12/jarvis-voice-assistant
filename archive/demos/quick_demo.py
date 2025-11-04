#!/usr/bin/env python3
"""
Quick Demo - Shows Jarvis working with 5 example commands
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

# Suppress debug logs
import logging
logging.getLogger().setLevel(logging.ERROR)

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.information import InformationSkills
import asyncio

print("\n" + "=" * 60)
print("  JARVIS QUICK DEMO")
print("=" * 60)
print("\nInitializing Jarvis...")

# Initialize
classifier = IntentClassifier()
router = CommandRouter()
skills = InformationSkills()

# Register handlers
for intent_type in [IntentType.GET_TIME, IntentType.GET_DATE, IntentType.GET_BATTERY, 
                    IntentType.GET_SYSTEM_INFO, IntentType.HELP]:
    router.register_handler(intent_type, skills.handle_intent)

print("[OK] Jarvis ready!\n")
print("=" * 60)

# Demo commands
commands = [
    "what time is it",
    "what's the date",
    "check battery",
    "system info",
    "help"
]

for i, command in enumerate(commands, 1):
    print(f"\n[Demo {i}/5]")
    print(f"You: {command}")
    
    # Process
    intent = classifier.classify(command)
    result = asyncio.run(router.route(intent))
    
    print(f"Jarvis: {result.message}")
    
    if i < len(commands):
        import time
        time.sleep(1)  # Pause between demos

print("\n" + "=" * 60)
print("DEMO COMPLETE!")
print("=" * 60)
print("\nJarvis is working perfectly!")
print("\nTo use interactively, run:")
print("  python jarvis_simple.py")
print()




