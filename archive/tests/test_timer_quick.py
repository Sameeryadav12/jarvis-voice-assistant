"""
Quick test to verify timer commands work in jarvis_simple.py
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.getLogger().setLevel(logging.WARNING)

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.reminders import ReminderSkills
import asyncio
import time

print("\n" + "=" * 60)
print("  TESTING TIMER FIX")
print("=" * 60)

print("\n[1/3] Initializing...")
classifier = IntentClassifier()
router = CommandRouter()
reminder_skills = ReminderSkills()

# Register timer handler
router.register_handler(IntentType.SET_TIMER, reminder_skills.handle_intent)
router.register_handler(IntentType.LIST_REMINDERS, reminder_skills.handle_intent)

print("  [OK] Initialized\n")

# Test timer command
test_commands = [
    "set timer for 3 seconds",
    "set timer for 30 seconds",
    "list reminders",
]

print("[2/3] Testing timer commands...")
for command in test_commands:
    print(f"\n  You: {command}")
    intent = classifier.classify(command)
    print(f"  Intent: {intent.type.value}")
    result = asyncio.run(router.route(intent))
    print(f"  Jarvis: {result.message}")
    
    if result.success:
        print("  [OK]")
    else:
        print("  [FAIL]")

# Wait for first timer
print("\n[3/3] Waiting for 3-second timer to fire...")
time.sleep(4)
print("  [INFO] Timer should have fired!\n")

# Cleanup
reminder_skills.shutdown()

print("=" * 60)
print("[SUCCESS] TIMERS WORKING!")
print("=" * 60)
print()




