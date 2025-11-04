"""
Test Jarvis volume control commands.
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

# Suppress debug logs
import logging
logging.getLogger().setLevel(logging.WARNING)

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.system import SystemSkills
from core.skills.information import InformationSkills
import asyncio

print("\n" + "=" * 60)
print("  JARVIS VOLUME CONTROL TEST")
print("=" * 60)
print("\nInitializing...")

# Initialize
classifier = IntentClassifier()
router = CommandRouter()
system_skills = SystemSkills()
info_skills = InformationSkills()

# Register handlers
system_intents = [
    IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, IntentType.VOLUME_SET,
    IntentType.MUTE, IntentType.UNMUTE
]
for intent_type in system_intents:
    router.register_handler(intent_type, system_skills.handle_intent)

router.register_handler(IntentType.GET_TIME, info_skills.handle_intent)

print("[OK] Jarvis initialized!\n")
print("=" * 60)

# Test commands
test_commands = [
    "what time is it",
    "set volume to 30",
    "turn up the volume",
    "turn down the volume",
    "mute",
    "unmute",
]

for i, command in enumerate(test_commands, 1):
    print(f"\n[Test {i}/{len(test_commands)}]")
    print(f"You: {command}")
    
    try:
        intent = classifier.classify(command)
        result = asyncio.run(router.route(intent))
        print(f"Jarvis: {result.message}")
        
        if not result.success and "not available" in result.message:
            print("  [INFO] This is expected if Windows API access is restricted")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    if i < len(test_commands):
        import time
        time.sleep(0.5)

print("\n" + "=" * 60)
print("VOLUME CONTROL TEST COMPLETE!")
print("=" * 60)
print()




