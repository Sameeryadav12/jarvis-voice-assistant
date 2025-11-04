@echo off
echo ============================================================
echo   JARVIS - Demo Mode
echo ============================================================
echo.
echo Starting Jarvis...
echo.

venv\Scripts\python.exe -c "from core.nlu.intents import IntentClassifier; from core.nlu.router import CommandRouter; from core.skills.information import InformationSkills; import asyncio; c = IntentClassifier(); r = CommandRouter(); s = InformationSkills(); r.register_handler('get_time', s.handle_intent); r.register_handler('help', s.handle_intent); r.register_handler('get_date', s.handle_intent); print('\n[DEMO] Testing Jarvis commands...\n'); commands = ['help', 'what time is it', 'what is the date']; for cmd in commands: intent = c.classify(cmd); result = asyncio.run(r.route(intent)); print(f'You: {cmd}'); print(f'Jarvis: {result.message}'); print()"

后才pause



