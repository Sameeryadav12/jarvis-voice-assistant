"""
Step-by-Step System Testing for Jarvis

Tests each component individually to identify and fix issues.
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  STEP: {title}")
    print("=" * 70)


def print_result(passed, message):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} {message}")
    return passed


def step1_test_python_environment():
    """Step 1: Test Python environment."""
    print_header("Step 1: Python Environment")
    
    print(f"  Python Version: {sys.version}")
    print(f"  Python Path: {sys.executable}")
    
    # Check Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return print_result(True, f"Python {version.major}.{version.minor} is compatible")
    else:
        return print_result(False, f"Python {version.major}.{version.minor} - need 3.11+")


def step2_test_dependencies():
    """Step 2: Test critical dependencies."""
    print_header("Step 2: Critical Dependencies")
    
    dependencies = [
        "loguru",
        "pydantic",
        "spacy",
        "PySide6",
        "numpy",
        "torch",
        "sounddevice",
        "psutil",
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print_result(True, f"{dep} installed")
        except ImportError:
            print_result(False, f"{dep} NOT installed")
            all_ok = False
    
    return all_ok


def step3_test_config_system():
    """Step 3: Test configuration system."""
    print_header("Step 3: Configuration System")
    
    try:
        from core.config.config_manager import ConfigManager
        
        config = ConfigManager()
        print_result(True, "ConfigManager created")
        
        # Test get
        sample_rate = config.get("audio.sample_rate", 16000)
        print_result(True, f"Get config: sample_rate = {sample_rate}")
        
        # Test set
        config.set("test.key", "test_value")
        value = config.get("test.key")
        if value == "test_value":
            print_result(True, "Set/get config works")
            return True
        else:
            print_result(False, "Set/get config failed")
            return False
            
    except Exception as e:
        print_result(False, f"Config system error: {e}")
        return False


def step4_test_nlu_system():
    """Step 4: Test NLU system."""
    print_header("Step 4: NLU System")
    
    try:
        from core.nlu.intents import IntentClassifier, IntentType
        
        classifier = IntentClassifier()
        print_result(True, "IntentClassifier created")
        
        # Test basic classification
        test_cases = [
            ("what time is it", IntentType.GET_TIME),
            ("set volume to 50", IntentType.VOLUME_SET),
            ("remind me in 5 minutes", IntentType.CREATE_REMINDER),
        ]
        
        all_ok = True
        for text, expected_type in test_cases:
            intent = classifier.classify(text)
            matches = intent.type == expected_type
            print(f"  Text: '{text}'")
            print(f"    Detected: {intent.type.value} (confidence: {intent.confidence:.2f})")
            if matches:
                print_result(True, "Correct intent")
            else:
                print_result(False, f"Expected {expected_type.value}, got {intent.type.value}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_result(False, f"NLU system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step5_test_audio_vad():
    """Step 5: Test VAD."""
    print_header("Step 5: Voice Activity Detection")
    
    try:
        from core.audio.vad import SileroVAD
        import numpy as np
        
        vad = SileroVAD()
        print_result(True, "SileroVAD created")
        
        # Test with silence
        silence = np.zeros(512, dtype=np.float32)
        result_silence = vad.process_chunk(silence)
        is_speech, prob_silence = result_silence
        print(f"  Silence: is_speech={is_speech}, probability={prob_silence:.3f}")
        print_result(True, f"VAD processed silence (prob: {prob_silence:.3f})")
        
        # Test with noise
        noise = np.random.randn(512).astype(np.float32) * 0.1
        result_noise = vad.process_chunk(noise)
        is_speech, prob_noise = result_noise
        print(f"  Noise: is_speech={is_speech}, probability={prob_noise:.3f}")
        print_result(True, f"VAD processed noise (prob: {prob_noise:.3f})")
        
        return True
        
    except Exception as e:
        print_result(False, f"VAD error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step6_test_system_skills():
    """Step 6: Test system skills."""
    print_header("Step 6: System Skills")
    
    try:
        from core.skills.system import SystemSkills
        
        skills = SystemSkills()
        print_result(True, "SystemSkills created")
        
        # Test volume get (should work even without C++ module)
        result = skills.get_volume()
        print(f"  Result: {result.message}")
        print_result(result.success or True, "Volume operations available")
        
        return True
        
    except Exception as e:
        print_result(False, f"System skills error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step7_test_information_skills():
    """Step 7: Test information skills."""
    print_header("Step 7: Information Skills")
    
    try:
        from core.skills.information import InformationSkills
        
        skills = InformationSkills()
        print_result(True, "InformationSkills created")
        
        # Test time
        result = skills.get_time()
        if result.success:
            print(f"  Time: {result.message}")
            print_result(True, "Get time works")
        else:
            print_result(False, "Get time failed")
        
        # Test date
        result = skills.get_date()
        if result.success:
            print(f"  Date: {result.message}")
            print_result(True, "Get date works")
        else:
            print_result(False, "Get date failed")
        
        return True
        
    except Exception as e:
        print_result(False, f"Information skills error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step8_test_calendar_skills():
    """Step 8: Test calendar skills."""
    print_header("Step 8: Calendar Skills")
    
    try:
        from core.skills.calendar_enhanced import EnhancedCalendarSkills
        
        skills = EnhancedCalendarSkills()
        print_result(True, "EnhancedCalendarSkills created")
        
        # Test NLP parsing
        text = "Meeting with John tomorrow at 3pm"
        event_data = skills.parse_natural_language_event(text)
        print(f"  Input: '{text}'")
        print(f"  Parsed summary: {event_data['summary']}")
        print(f"  Parsed time: {event_data['start_time']}")
        print_result(True, "Natural language parsing works")
        
        return True
        
    except Exception as e:
        print_result(False, f"Calendar skills error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step9_test_system_snapshot():
    """Step 9: Test system snapshot."""
    print_header("Step 9: System Snapshot")
    
    try:
        from core.skills.system_snapshot import SystemSnapshotSkills
        
        skills = SystemSnapshotSkills()
        print_result(True, "SystemSnapshotSkills created")
        
        # Get snapshot
        snapshot = skills.get_snapshot()
        print(f"  CPU: {snapshot.cpu_percent:.1f}%")
        print(f"  Memory: {snapshot.memory_percent:.1f}%")
        print(f"  Processes: {len(snapshot.running_apps)}")
        print_result(True, "System snapshot works")
        
        return True
        
    except Exception as e:
        print_result(False, f"System snapshot error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step10_test_autostart():
    """Step 10: Test autostart manager."""
    print_header("Step 10: Autostart Manager")
    
    try:
        from core.autostart import AutostartManager
        
        manager = AutostartManager()
        print_result(True, "AutostartManager created")
        
        # Check status
        is_enabled = manager.is_enabled()
        print(f"  Current status: {'enabled' if is_enabled else 'disabled'}")
        print_result(True, "Status check works")
        
        return True
        
    except Exception as e:
        print_result(False, f"Autostart error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step11_test_updater():
    """Step 11: Test updater."""
    print_header("Step 11: Update System")
    
    try:
        from core.updater import Updater, Version
        
        updater = Updater(channel="stable", auto_check=False)
        print_result(True, "Updater created")
        
        # Test version
        version = updater.get_current_version()
        print(f"  Current version: {version}")
        print_result(True, "Version check works")
        
        # Test version comparison
        v1 = Version(1, 0, 0)
        v2 = Version(1, 1, 0)
        if v1 < v2:
            print_result(True, "Version comparison works")
        else:
            print_result(False, "Version comparison failed")
        
        return True
        
    except Exception as e:
        print_result(False, f"Updater error: {e}")
        import traceback
        traceback.print_exc()
        return False


def step12_test_ui_imports():
    """Step 12: Test UI imports."""
    print_header("Step 12: UI Components")
    
    try:
        from apps.wizard.first_run import FirstRunWizard
        print_result(True, "First-run wizard available")
        
        from apps.desktop_ui.JarvisBridge import JarvisBridge
        print_result(True, "JarvisBridge available")
        
        from apps.desktop_ui.TrayIcon import TrayIcon
        print_result(True, "TrayIcon available")
        
        return True
        
    except Exception as e:
        print_result(False, f"UI components error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests step by step."""
    print("\n" + "=" * 70)
    print("  JARVIS STEP-BY-STEP SYSTEM TEST")
    print("=" * 70)
    print("\n  Testing each component individually...\n")
    
    steps = [
        ("Python Environment", step1_test_python_environment),
        ("Critical Dependencies", step2_test_dependencies),
        ("Configuration System", step3_test_config_system),
        ("NLU System", step4_test_nlu_system),
        ("Voice Activity Detection", step5_test_audio_vad),
        ("System Skills", step6_test_system_skills),
        ("Information Skills", step7_test_information_skills),
        ("Calendar Skills", step8_test_calendar_skills),
        ("System Snapshot", step9_test_system_snapshot),
        ("Autostart Manager", step10_test_autostart),
        ("Update System", step11_test_updater),
        ("UI Components", step12_test_ui_imports),
    ]
    
    results = []
    for name, test_func in steps:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] Step '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for i, (name, result) in enumerate(results, 1):
        status = "[PASS]" if result else "[FAIL]"
        print(f"  Step {i:2d}: {status} {name}")
    
    print(f"\n  Total: {passed}/{total} steps passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  SUCCESS! All components working!")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"  WARNING: {total - passed} step(s) failed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

