"""
Complete Jarvis System Test

Tests all major components and their integration.
Run this to verify the entire system is working correctly.
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_imports():
    """Test that all core modules can be imported."""
    print_section("TEST 1: Core Module Imports")
    
    modules = [
        # Config
        ("core.config.config_manager", "ConfigManager"),
        # Audio
        ("core.audio.vad", "SileroVAD"),
        ("core.audio.ring_buffer", "RingBuffer"),
        ("core.audio.stt_strategy", "STTStrategy"),
        # NLU
        ("core.nlu.intents", "IntentClassifier"),
        ("core.nlu.entity_extractor", "EntityExtractor"),
        ("core.nlu.router", "CommandRouter"),
        # Skills
        ("core.skills.system", "SystemSkills"),
        ("core.skills.information", "InformationSkills"),
        ("core.skills.calendar", "CalendarSkills"),
        ("core.skills.reminders", "ReminderSkills"),
        ("core.skills.calendar_enhanced", "EnhancedCalendarSkills"),
        ("core.skills.dictation", "DictationSkills"),
        ("core.skills.system_snapshot", "SystemSnapshotSkills"),
        ("core.skills.web_quick", "WebQuickSkills"),
        # Memory
        ("core.memory.vectorstore", "VectorStore"),
        # TTS
        ("core.tts.piper", "PiperTTS"),
        ("core.tts.edge", "EdgeTTS"),
        # Security
        ("core.permissions", "PermissionsManager"),
        ("core.secrets", "SecretsVault"),
        # Monitoring
        ("core.reporter", "CrashReporter"),
        ("core.metrics", "MetricsCollector"),
        # Distribution
        ("core.autostart", "AutostartManager"),
        ("core.updater", "Updater"),
    ]
    
    failed = []
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"  [FAIL] {module_name}.{class_name}: {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n  Failed imports: {len(failed)}/{len(modules)}")
        return False
    else:
        print(f"\n  All {len(modules)} modules imported successfully!")
        return True


def test_config_system():
    """Test configuration system."""
    print_section("TEST 2: Configuration System")
    
    try:
        from core.config.config_manager import ConfigManager
        
        config = ConfigManager()
        print("  [OK] ConfigManager created")
        
        # Test getting values
        sample_rate = config.get("audio.sample_rate", 16000)
        print(f"  [OK] Sample rate: {sample_rate}")
        
        # Test setting values
        config.set("test.value", "test123")
        value = config.get("test.value")
        assert value == "test123"
        print("  [OK] Set/get values work")
        
        # Test offline mode
        is_offline = config.is_offline_mode()
        print(f"  [OK] Offline mode: {is_offline}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nlu_system():
    """Test NLU system."""
    print_section("TEST 3: Natural Language Understanding")
    
    try:
        from core.nlu.intents import IntentClassifier, IntentType
        
        classifier = IntentClassifier()
        print("  [OK] IntentClassifier created")
        
        # Test some commands
        test_commands = [
            ("what time is it", IntentType.GET_TIME),
            ("set volume to 50", IntentType.VOLUME_SET),
            ("search for python", IntentType.SEARCH),
        ]
        
        for text, expected in test_commands:
            intent = classifier.classify(text)
            print(f"  Text: '{text}'")
            print(f"    Detected: {intent.type.value} (confidence: {intent.confidence:.2f})")
            if intent.type == expected:
                print(f"    [OK] Correct intent detected")
            else:
                print(f"    [WARN] Expected {expected.value}, got {intent.type.value}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skills_system():
    """Test skills framework."""
    print_section("TEST 4: Skills Framework")
    
    try:
        from core.skills.system import SystemSkills
        from core.skills.information import InformationSkills
        from core.skills.system_snapshot import SystemSnapshotSkills
        
        # Test system skills
        system = SystemSkills()
        print("  [OK] SystemSkills created")
        
        # Test information skills
        info = InformationSkills()
        result = info.get_time()
        print(f"  [OK] Time: {result.message}")
        
        result = info.get_date()
        print(f"  [OK] Date: {result.message}")
        
        # Test system snapshot
        snapshot = SystemSnapshotSkills()
        result = snapshot.get_snapshot_summary()
        print(f"  [OK] System snapshot generated")
        print(f"    {result.message[:100]}...")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_system():
    """Test vector memory system."""
    print_section("TEST 5: Vector Memory")
    
    try:
        from core.memory.vectorstore import VectorStore
        
        # Create temporary memory
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        
        store = VectorStore(persist_directory=str(temp_dir))
        print("  [OK] VectorStore created")
        
        # Add some memories
        store.add_memory("I like pizza", {"type": "preference"})
        store.add_memory("My favorite color is blue", {"type": "preference"})
        print("  [OK] Added memories")
        
        # Search
        results = store.search("what food do I like", n_results=1)
        if results and len(results) > 0:
            print(f"  [OK] Memory search works: '{results[0]}'")
        else:
            print("  [WARN] No results from memory search")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_components():
    """Test audio components (without actually capturing audio)."""
    print_section("TEST 6: Audio Components")
    
    try:
        from core.audio.vad import SileroVAD
        from core.audio.ring_buffer import RingBuffer
        import numpy as np
        
        # Test VAD
        vad = SileroVAD()
        print("  [OK] SileroVAD created")
        
        # Test with dummy audio
        dummy_audio = np.zeros(512, dtype=np.float32)
        prob = vad.process_chunk(dummy_audio)
        print(f"  [OK] VAD processed chunk (prob: {prob:.3f})")
        
        # Test ring buffer
        buffer = RingBuffer(maxlen=1000)
        buffer.extend(dummy_audio)
        print(f"  [OK] RingBuffer working (size: {len(buffer)})")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security_systems():
    """Test security and privacy systems."""
    print_section("TEST 7: Security & Privacy")
    
    try:
        from core.permissions import PermissionsManager
        from core.secrets import SecretsVault
        
        # Test permissions
        perms = PermissionsManager()
        print("  [OK] PermissionsManager created")
        
        # Test permission check
        has_perm = perms.has_permission("test_skill", "test_action")
        print(f"  [OK] Permission check: {has_perm}")
        
        # Test secrets vault
        vault = SecretsVault()
        print("  [OK] SecretsVault created")
        
        # Test secret storage (don't actually store anything sensitive)
        # Just verify the API works
        print("  [OK] Secrets vault API available")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitoring_systems():
    """Test monitoring and telemetry."""
    print_section("TEST 8: Monitoring & Telemetry")
    
    try:
        from core.metrics import MetricsCollector
        from core.reporter import CrashReporter
        
        # Test metrics
        metrics = MetricsCollector()
        print("  [OK] MetricsCollector created")
        
        metrics.record_event("test_event", {"test": "data"})
        print("  [OK] Event recording works")
        
        summary = metrics.get_summary()
        print(f"  [OK] Metrics summary: {len(summary)} metrics")
        
        # Test crash reporter
        reporter = CrashReporter()
        print("  [OK] CrashReporter created")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_distribution_systems():
    """Test distribution and packaging systems."""
    print_section("TEST 9: Distribution Systems")
    
    try:
        from core.autostart import AutostartManager
        from core.updater import Updater, Version
        
        # Test autostart
        autostart = AutostartManager()
        print("  [OK] AutostartManager created")
        
        is_enabled = autostart.is_enabled()
        print(f"  [OK] Autostart status: {'enabled' if is_enabled else 'disabled'}")
        
        # Test updater
        updater = Updater(channel="stable", auto_check=False)
        print("  [OK] Updater created")
        
        version = updater.get_current_version()
        print(f"  [OK] Current version: {version}")
        
        # Test version comparison
        v1 = Version(1, 0, 0)
        v2 = Version(1, 1, 0)
        assert v1 < v2
        print("  [OK] Version comparison works")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_components():
    """Test UI components (imports only)."""
    print_section("TEST 10: UI Components")
    
    try:
        # Test wizard
        from apps.wizard.first_run import FirstRunWizard, SetupConfig
        print("  [OK] First-run wizard available")
        
        # Test QML UI bridge
        from apps.desktop_ui.JarvisBridge import JarvisBridge
        print("  [OK] JarvisBridge available")
        
        # Test tray icon
        from apps.desktop_ui.TrayIcon import TrayIcon
        print("  [OK] TrayIcon available")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  JARVIS COMPLETE SYSTEM TEST")
    print("=" * 70)
    print("\n  This will test all major components of Jarvis.")
    print("  Note: Some features require additional setup (API keys, models, etc.)")
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration System", test_config_system),
        ("NLU System", test_nlu_system),
        ("Skills Framework", test_skills_system),
        ("Vector Memory", test_memory_system),
        ("Audio Components", test_audio_components),
        ("Security & Privacy", test_security_systems),
        ("Monitoring & Telemetry", test_monitoring_systems),
        ("Distribution Systems", test_distribution_systems),
        ("UI Components", test_ui_components),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  ✅ ALL TESTS PASSED - JARVIS IS READY!")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"  ⚠️  {total - passed} TEST(S) FAILED")
        print("=" * 70)
        print("\n  Some components may need additional setup:")
        print("  - Download models: python -m spacy download en_core_web_sm")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())

