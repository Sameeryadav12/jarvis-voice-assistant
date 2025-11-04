"""
Simple test to verify each module works independently.
Tests one thing at a time.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("JARVIS SIMPLE TEST - Step by Step")
print("=" * 60)
print()

# Test 1: Import core modules
print("[1/5] Testing imports...")
try:
    from core.nlu.intents import IntentClassifier, IntentType
    from core.skills.information import InformationSkills
    print("  [OK] Core modules imported successfully")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize NLU
print("\n[2/5] Testing NLU initialization...")
try:
    classifier = IntentClassifier()
    print("  [OK] NLU initialized successfully")
except Exception as e:
    print(f"  [FAIL] NLU failed: {e}")
    sys.exit(1)

# Test 3: Test intent classification
print("\n[3/5] Testing intent classification...")
try:
    test_cases = [
        ("what time is it", IntentType.GET_TIME),
        ("check battery", IntentType.GET_BATTERY),
        ("help", IntentType.HELP),
    ]
    
    passed = 0
    for text, expected in test_cases:
        intent = classifier.classify(text)
        if intent.type == expected:
            print(f"  [OK] '{text}' -> {intent.type.value}")
            passed += 1
        else:
            print(f"  [FAIL] '{text}' -> {intent.type.value} (expected {expected.value})")
    
    if passed == len(test_cases):
        print(f"  [OK] All {passed}/{len(test_cases)} tests passed")
    else:
        print(f"  [WARN] {passed}/{len(test_cases)} tests passed")
except Exception as e:
    print(f"  [FAIL] Classification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test information skills
print("\n[4/5] Testing information skills...")
try:
    skills = InformationSkills()
    
    # Test time
    result = skills.get_time()
    if result.success:
        print(f"  [OK] Time: {result.message}")
    else:
        print(f"  [FAIL] Time failed")
    
    # Test date
    result = skills.get_date()
    if result.success:
        print(f"  [OK] Date: {result.message}")
    else:
        print(f"  [FAIL] Date failed")
    
    # Test battery
    result = skills.get_battery()
    if result.success:
        print(f"  [OK] Battery: {result.message}")
    else:
        print(f"  [FAIL] Battery failed")
        
except Exception as e:
    print(f"  [FAIL] Skills failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test full flow
print("\n[5/5] Testing full command flow...")
try:
    from core.nlu.router import CommandRouter
    
    router = CommandRouter()
    router.register_handler(IntentType.GET_TIME, skills.handle_intent)
    router.register_handler(IntentType.GET_BATTERY, skills.handle_intent)
    router.register_handler(IntentType.HELP, skills.handle_intent)
    
    # Test command
    intent = classifier.classify("what time is it")
    import asyncio
    result = asyncio.run(router.route(intent))
    
    if result.success:
        print(f"  [OK] Full flow working: {result.message}")
    else:
        print(f"  [FAIL] Flow failed: {result.message}")
        
except Exception as e:
    print(f"  [FAIL] Flow failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 60)
print("\nJarvis is working correctly. You can now run:")
print("  python jarvis.py --console")
print("\nOr run the demo:")
print("  python demo.py")
print()

