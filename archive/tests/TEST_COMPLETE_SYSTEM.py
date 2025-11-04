#!/usr/bin/env python
"""Complete system test for Jarvis."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("JARVIS COMPLETE SYSTEM TEST")
print("=" * 60)

# Test 1: Environment
print("\n[TEST 1] Checking environment...")
try:
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print("[OK] Environment check passed")
except Exception as e:
    print(f"[ERROR] Environment check failed: {e}")
    sys.exit(1)

# Test 2: Core imports
print("\n[TEST 2] Testing core imports...")
try:
    from core.nlu import IntentClassifier, IntentType
    from core.bindings import windows_native
    print("[OK] Core imports successful")
except Exception as e:
    print(f"[ERROR] Core imports failed: {e}")
    sys.exit(1)

# Test 3: NLU
print("\n[TEST 3] Testing NLU...")
try:
    classifier = IntentClassifier()
    result = classifier.classify("what time is it")
    print(f"[OK] NLU working - Intent: {result.type}")
except Exception as e:
    print(f"[ERROR] NLU failed: {e}")
    sys.exit(1)

# Test 4: Bindings
print("\n[TEST 4] Testing bindings...")
try:
    vol = windows_native.get_master_volume()
    print(f"[OK] Bindings working - Volume: {vol*100:.1f}%")
except Exception as e:
    print(f"[ERROR] Bindings failed: {e}")
    sys.exit(1)

# Test 5: Skills
print("\n[TEST 5] Testing skills...")
try:
    from core.skills.information import InformationSkills
    from core.skills.system import SystemSkills
    from core.skills.reminders import ReminderSkills
    print("[OK] All skills imported successfully")
except Exception as e:
    print(f"[ERROR] Skills import failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All tests passed!")
print("=" * 60)

