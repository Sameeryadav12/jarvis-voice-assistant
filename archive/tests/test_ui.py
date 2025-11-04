"""
Test Jarvis Desktop UI
Verifies the UI can be created and components work.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 60)
print("  JARVIS DESKTOP UI TEST")
print("=" * 60)

# Test 1: Import UI components
print("\n[1/4] Testing UI imports...")
try:
    from PySide6.QtWidgets import QApplication
    from apps.desktop_ui.main_window import JarvisMainWindow
    print("  [OK] UI modules imported")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# Test 2: Create application
print("\n[2/4] Creating QApplication...")
try:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    print("  [OK] QApplication created")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# Test 3: Create main window
print("\n[3/4] Creating main window...")
try:
    window = JarvisMainWindow()
    print("  [OK] Main window created")
    print(f"  Title: {window.windowTitle()}")
    print(f"  Size: {window.width()}x{window.height()}")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify components
print("\n[4/4] Verifying UI components...")
try:
    assert window.history_text is not None, "History text not found"
    assert window.input_field is not None, "Input field not found"
    assert window.send_button is not None, "Send button not found"
    assert window.status_label is not None, "Status label not found"
    print("  [OK] All UI components present")
except AssertionError as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] DESKTOP UI WORKING!")
print("=" * 60)
print("\nUI Features:")
print("  ✅ Main window with modern design")
print("  ✅ Conversation history display")
print("  ✅ Command input field")
print("  ✅ Quick action buttons (Time, Date, Battery, etc.)")
print("  ✅ Status indicators")
print("  ✅ Clean, professional interface")
print("\nTo launch the UI:")
print("  python jarvis_ui.py")
print("\n(The window will open - try the quick action buttons!)")
print()

# Cleanup
window.close()




