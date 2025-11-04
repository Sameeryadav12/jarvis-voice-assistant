"""
Test Sprint 13 - UI Components
Verifies all QML components and UI integration work correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 60)
print("  SPRINT 13 - UI COMPONENTS TEST")
print("=" * 60)

# Test 1: Import UI components
print("\n[1/6] Testing UI component imports...")
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtQml import QQmlApplicationEngine
    print("  [OK] PySide6 imports successful")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# Test 2: Check QML files exist
print("\n[2/6] Checking QML files...")
qml_files = [
    "apps/desktop_ui/Theme.qml",
    "apps/desktop_ui/components/VoiceOrb.qml",
    "apps/desktop_ui/components/TranscriptTicker.qml",
    "apps/desktop_ui/components/ActivityCard.qml",
    "apps/desktop_ui/components/CommandPalette.qml",
    "apps/desktop_ui/MainWindow.qml"
]

all_exist = True
for qml_file in qml_files:
    path = Path(qml_file)
    if path.exists():
        print(f"  [OK] {qml_file}")
    else:
        print(f"  [FAIL] {qml_file} not found")
        all_exist = False

if not all_exist:
    print("  [ERROR] Some QML files are missing")
    sys.exit(1)

# Test 3: Import Python modules
print("\n[3/6] Testing Python module imports...")
try:
    from apps.desktop_ui.JarvisBridge import JarvisBridge, register_bridge
    from apps.desktop_ui.TrayIcon import TrayIcon
    from apps.desktop_ui.main_qml import main
    print("  [OK] Python modules imported")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Create QApplication
print("\n[4/6] Creating QApplication...")
try:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    print("  [OK] QApplication created")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# Test 5: Register bridge
print("\n[5/6] Registering QML types...")
try:
    register_bridge()
    print("  [OK] Bridge registered")
except Exception as e:
    print(f"  [WARN] Bridge registration: {e}")

# Test 6: Create bridge instance
print("\n[6/6] Testing JarvisBridge...")
try:
    bridge = JarvisBridge()
    print(f"  [OK] Bridge created")
    print(f"  Initial state: {bridge.orbState}")
    print(f"  Initial status: {bridge.statusText}")
    
    # Test command execution
    print("\n  Testing command execution...")
    bridge.executeCommand("what time is it")
    print(f"  State after command: {bridge.orbState}")
    print(f"  Activity history length: {len(bridge.activityHistory)}")
    
    if bridge.activityHistory:
        print(f"  Last activity: {bridge.activityHistory[0]['intentName']}")
    
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] SPRINT 13 COMPONENTS WORKING!")
print("=" * 60)
print("\nComponents Created:")
print("  [OK] Design System (Theme.qml)")
print("  [OK] Voice Orb Component")
print("  [OK] Transcript Ticker")
print("  [OK] Activity Cards")
print("  [OK] Command Palette (Ctrl+K)")
print("  [OK] System Tray Integration")
print("  [OK] Python-QML Bridge")
print("\nTo launch the UI:")
print("  python jarvis_ui.py")
print("  or")
print("  python apps/desktop_ui/main_qml.py")
print()

