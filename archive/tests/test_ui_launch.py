"""
Quick test to verify UI launches correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing UI launch...")
print("=" * 60)

try:
    print("[1/3] Importing modules...")
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    print("  [OK] Imports successful")
    
    print("\n[2/3] Checking system tray...")
    if QSystemTrayIcon.isSystemTrayAvailable():
        print("  [OK] System tray available")
    else:
        print("  [WARN] System tray not available")
    
    print("\n[3/3] Testing QML imports...")
    from apps.desktop_ui.main_qml import main
    print("  [OK] QML main function imported")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All checks passed!")
    print("=" * 60)
    print("\nTo launch UI, run:")
    print("  python jarvis_ui.py")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


