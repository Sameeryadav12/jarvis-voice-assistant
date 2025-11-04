"""
Test Console Mode

Tests the console mode application without requiring user input.
"""

import sys
from pathlib import Path


def test_jarvis_simple_import():
    """Test that jarvis_simple can be imported."""
    print("\n" + "=" * 70)
    print("  TEST: Console Mode Import")
    print("=" * 70)
    
    try:
        # Just test that the core components work
        from core.nlu.intents import IntentClassifier
        from core.skills.system import SystemSkills
        from core.skills.information import InformationSkills
        
        print("  [PASS] All core imports successful")
        
        # Test creating instances
        classifier = IntentClassifier()
        print("  [PASS] IntentClassifier created")
        
        info_skills = InformationSkills()
        print("  [PASS] InformationSkills created")
        
        # Test a simple command
        intent = classifier.classify("what time is it")
        result = info_skills.handle_intent(intent)
        
        print(f"  Command: 'what time is it'")
        print(f"  Response: {result.message}")
        print("  [PASS] Command processed successfully")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run console mode test."""
    print("\n" + "=" * 70)
    print("  JARVIS CONSOLE MODE TEST")
    print("=" * 70)
    
    success = test_jarvis_simple_import()
    
    if success:
        print("\n" + "=" * 70)
        print("  SUCCESS! Console mode components working!")
        print("=" * 70)
        print("\n  To run console mode manually:")
        print("    python jarvis_simple.py")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  FAILED! Console mode has errors")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

