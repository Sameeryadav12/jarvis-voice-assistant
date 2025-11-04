"""
Test Sprint 16: Packaging & Distribution

Tests:
- S16-01: MSIX Package
- S16-02: Inno Setup Installer
- S16-03: First-Run Wizard
- S16-04: Autostart & System Tray
- S16-05: Update Channel
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def test_msix_package():
    """Test S16-01: MSIX Package."""
    print("\n" + "=" * 60)
    print("TEST S16-01: MSIX Package")
    print("=" * 60)
    
    try:
        print("\n[1/3] Checking MSIX manifest...")
        manifest_path = Path("packaging/AppxManifest.xml")
        assert manifest_path.exists(), "AppxManifest.xml not found"
        
        # Parse manifest
        import xml.etree.ElementTree as ET
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        print(f"  Manifest found: {manifest_path}")
        print("  [OK] MSIX manifest exists")
        
        print("\n[2/3] Checking build script...")
        build_script = Path("packaging/build_msix.py")
        assert build_script.exists(), "build_msix.py not found"
        print(f"  Build script found: {build_script}")
        print("  [OK] Build script exists")
        
        print("\n[3/3] Validating structure...")
        # Just check file exists and is readable
        with open(build_script) as f:
            content = f.read()
            assert "makeappx" in content
            assert "PyInstaller" in content
        print("  [OK] Build script structure valid")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S16-01: MSIX Package - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inno_setup():
    """Test S16-02: Inno Setup Installer."""
    print("\n" + "=" * 60)
    print("TEST S16-02: Inno Setup Installer")
    print("=" * 60)
    
    try:
        print("\n[1/2] Checking Inno Setup script...")
        iss_path = Path("packaging/Jarvis.iss")
        assert iss_path.exists(), "Jarvis.iss not found"
        print(f"  Script found: {iss_path}")
        print("  [OK] Inno Setup script exists")
        
        print("\n[2/2] Validating script content...")
        with open(iss_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "AppName" in content
            assert "AppVersion" in content
            assert "[Setup]" in content
            assert "[Files]" in content
            assert "[Icons]" in content
        print("  [OK] Script structure valid")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S16-02: Inno Setup - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_first_run_wizard():
    """Test S16-03: First-Run Wizard."""
    print("\n" + "=" * 60)
    print("TEST S16-03: First-Run Wizard")
    print("=" * 60)
    
    try:
        print("\n[1/3] Importing wizard module...")
        from apps.wizard.first_run import FirstRunWizard, SetupConfig
        print("  [OK] Wizard module imported")
        
        print("\n[2/3] Testing SetupConfig dataclass...")
        config = SetupConfig()
        assert config.wake_word_enabled == True
        assert config.stt_backend == "offline"
        print("  [OK] SetupConfig works")
        
        print("\n[3/3] Testing wizard pages...")
        from apps.wizard.first_run import (
            WelcomePage, AudioDevicePage, WakeWordPage,
            STTTTSPage, PrivacyPage, CompletionPage
        )
        print("  Found 6 wizard pages")
        print("  [OK] Wizard pages defined")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S16-03: First-Run Wizard - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_autostart():
    """Test S16-04: Autostart & System Tray."""
    print("\n" + "=" * 60)
    print("TEST S16-04: Autostart & System Tray")
    print("=" * 60)
    
    try:
        print("\n[1/3] Importing autostart module...")
        from core.autostart import AutostartManager
        print("  [OK] Autostart module imported")
        
        print("\n[2/3] Creating autostart manager...")
        manager = AutostartManager()
        print(f"  Executable path: {manager.executable_path}")
        print("  [OK] Autostart manager created")
        
        print("\n[3/3] Testing status check...")
        # Just check that the method doesn't crash
        status = manager.is_enabled()
        print(f"  Current status: {'enabled' if status else 'disabled'}")
        print("  [OK] Status check works")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S16-04: Autostart - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_updater():
    """Test S16-05: Update Channel."""
    print("\n" + "=" * 60)
    print("TEST S16-05: Update Channel")
    print("=" * 60)
    
    try:
        print("\n[1/4] Importing updater module...")
        from core.updater import Updater, Version, UpdateInfo
        print("  [OK] Updater module imported")
        
        print("\n[2/4] Testing Version class...")
        v1 = Version(1, 0, 0)
        v2 = Version(1, 1, 0)
        assert v1 < v2
        assert str(v1) == "1.0.0"
        
        v3 = Version.from_string("2.3.4")
        assert v3.major == 2
        assert v3.minor == 3
        assert v3.patch == 4
        print("  [OK] Version class works")
        
        print("\n[3/4] Creating updater...")
        updater = Updater(channel="stable", auto_check=False)
        print(f"  Channel: {updater.channel}")
        print(f"  Current version: {updater.get_current_version()}")
        print("  [OK] Updater created")
        
        print("\n[4/4] Testing update check logic...")
        # Should not check because auto_check is False
        should_check = updater.should_check_for_updates()
        assert should_check == False
        print("  [OK] Update check logic works")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S16-05: Updater - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Sprint 16 tests."""
    print("\n" + "=" * 60)
    print("SPRINT 16: PACKAGING & DISTRIBUTION - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test S16-01
    results.append(("S16-01: MSIX Package", test_msix_package()))
    
    # Test S16-02
    results.append(("S16-02: Inno Setup", test_inno_setup()))
    
    # Test S16-03
    results.append(("S16-03: First-Run Wizard", test_first_run_wizard()))
    
    # Test S16-04
    results.append(("S16-04: Autostart", test_autostart()))
    
    # Test S16-05
    results.append(("S16-05: Updater", test_updater()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL SPRINT 16 TESTS PASSED!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("[WARNING] SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

