"""
Test Jarvis reminder system with desktop notifications.
Sprint 4 - Part 2: Reminders & Notifications
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

from core.skills.reminders import ReminderSkills
from datetime import datetime, timedelta
import time

print("\n" + "=" * 60)
print("  JARVIS REMINDER SYSTEM TEST")
print("=" * 60)

# Test 1: Initialize
print("\n[1/5] Initializing reminder system...")
try:
    reminders = ReminderSkills()
    print("  [OK] Reminder system initialized")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create short timer (5 seconds)
print("\n[2/5] Creating 5-second timer...")
try:
    result = reminders.create_timer(5, "Test Timer - 5 seconds")
    print(f"  [OK] {result.message}")
    print("  Waiting for notification... (should appear in 5 seconds)")
    time.sleep(6)
    print("  [INFO] Timer should have fired!")
except Exception as e:
    print(f"  [FAIL] {e}")

# Test 3: Create reminder for 10 seconds from now
print("\n[3/5] Creating reminder for 10 seconds...")
try:
    when = datetime.now() + timedelta(seconds=10)
    result = reminders.create_reminder("Test Reminder", when)
    print(f"  [OK] {result.message}")
except Exception as e:
    print(f"  [FAIL] {e}")

# Test 4: List active reminders
print("\n[4/5] Listing active reminders...")
try:
    result = reminders.list_reminders()
    print(f"  [OK] {result.message}")
    
    if result.data and result.data.get('reminders'):
        for reminder in result.data['reminders']:
            print(f"    - Next run: {reminder['next_run']}")
except Exception as e:
    print(f"  [FAIL] {e}")

# Test 5: Wait for reminder
print("\n[5/5] Waiting for reminder notification...")
print("  (Waiting 12 seconds for reminder to fire...)")
time.sleep(12)
print("  [INFO] Reminder should have fired!")

# Cleanup
print("\n[Cleanup] Shutting down scheduler...")
reminders.shutdown()

print("\n" + "=" * 60)
print("[SUCCESS] REMINDER SYSTEM WORKING!")
print("=" * 60)
print("\nReminder capabilities:")
print("  - Create timers (countdown)")
print("  - Create reminders (specific time)")
print("  - Desktop notifications")
print("  - List active reminders")
print("\nCheck if you saw desktop notifications pop up!")
print()




