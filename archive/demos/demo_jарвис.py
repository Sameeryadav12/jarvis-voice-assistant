#!/usr/bin/env python
"""Quick Jarvis demo."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from core.nlu.intents import IntentClassifier
from core.nlu.router import CommandRouter
from core.skills.information import InformationSkills
import asyncio

# Initialize
print("\n" + "=" * 70)
print("JARVIS DEMO")
print("=" * 70 + "\n")

classifier = IntentClassifier()
router = CommandRouter()
skills = InformationSkills()

# Register handlers
from core.nlu.intents import IntentType
router.register_handler(IntentType.GET_TIME, skills.handle_intent)
router.register_handler(IntentType.HELP, skills.handle_intent)
router.register_handler(IntentType.GET_DATE, skills.handle_intent)

# Test commands
commands = [
    'help',
    'what time is it',
    "what's the date"
]

for cmd in commands:
    intent = classifier.classify(cmd)
    result = asyncio.run(router.route(intent))
    print(f"You: {cmd}")
    print(f"Jarvis: {result.message}\n")

print("=" * 70)
print("Demo complete! Jarvis is working!")
print("=" * 70 + "\n")



