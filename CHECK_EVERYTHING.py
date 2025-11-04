#!/usr/bin/env python
"""Complete system check."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("JARVIS COMPLETE SYSTEM CHECK")
print("=" * 60)

errors = []
warnings = []

# Check 1: Imports
print("\n[CHECK 1] Testing imports...")
try:
    from core.nlu.intents import IntentType, IntentClassifier
    from core.bindings import windows_native
    from core.skills.information import InformationSkills
    from core.skills.system import SystemSkills
    print("  [OK] All imports successful")
except Exception as e:
    errors.append(f"Import error: {e}")
    print(f"  [ERROR] {e}")

# Check 2: Intent Count
print("\n[CHECK 2] Checking intent count...")
try:
    intent_count = len(list(IntentType))
    print(f"  [OK] Total intents: {intent_count}")
    if intent_count < 80:
        warnings.append(f"Expected 80+ intents, got {intent_count}")
except Exception as e:
    errors.append(f"Intent count error: {e}")

# Check 3: NLU Classification
print("\n[CHECK 3] Testing NLU...")
try:
    classifier = IntentClassifier()
    result = classifier.classify("help")
    print(f"  [OK] NLU working - Intent: {result.type}")
except Exception as e:
    errors.append(f"NLU error: {e}")

# Check 4: Bindings
print("\n[CHECK 4] Testing bindings...")
try:
    vol = windows_native.get_master_volume()
    print(f"  [OK] Bindings working - Volume: {vol*100:.1f}%")
except Exception as e:
    errors.append(f"Bindings error: {e}")

# Check 5: Skills
print("\n[CHECK 5] Testing skills...")
try:
    info = InformationSkills()
    print("  [OK] Information skills imported")
    system = SystemSkills()
    print("  [OK] System skills imported")
except Exception as e:
    errors.append(f"Skills error: {e}")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"[ERRORS: {len(errors)}]")
    for error in errors:
        print(f"  - {error}")
if warnings:
    print(f"[WARNINGS: {len(warnings)}]")
    for warning in warnings:
        print(f"  - {warning}")
if not errors and not warnings:
    print("[SUCCESS] All checks passed!")
print("=" * 60)



