"""
Step-by-step UI launch test
"""

import sys
from pathlib import Path

print("=" * 60)
print("STEP-BY-STEP UI TEST")
print("=" * 60)

# Step 1: Check Python imports
print("\n[STEP 1] Checking basic Python imports...")
try:
    import PySide6
    print("  [OK] PySide6 imported")
except Exception as e:
    print(f"  [FAIL] PySide6 import error: {e}")
    sys.exit(1)

# Step 2: Check QtWidgets
print("\n[STEP 2] Checking QtWidgets...")
try:
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    print("  [OK] QtWidgets imported")
except Exception as e:
    print(f"  [FAIL] QtWidgets import error: {e}")
    sys.exit(1)

# Step 3: Check QtQml
print("\n[STEP 3] Checking QtQml...")
try:
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
    print("  [OK] QtQml imported")
except Exception as e:
    print(f"  [FAIL] QtQml import error: {e}")
    sys.exit(1)

# Step 4: Check system tray
print("\n[STEP 4] Checking system tray availability...")
try:
    available = QSystemTrayIcon.isSystemTrayAvailable()
    print(f"  [OK] System tray available: {available}")
except Exception as e:
    print(f"  [FAIL] System tray check error: {e}")
    sys.exit(1)

# Step 5: Check QML files exist
print("\n[STEP 5] Checking QML files exist...")
try:
    ui_dir = Path(__file__).parent / "apps" / "desktop_ui"
    theme_file = ui_dir / "Theme.qml"
    main_file = ui_dir / "MainWindow.qml"
    
    if theme_file.exists():
        print(f"  [OK] Theme.qml exists")
    else:
        print(f"  [FAIL] Theme.qml not found at {theme_file}")
        sys.exit(1)
    
    if main_file.exists():
        print(f"  [OK] MainWindow.qml exists")
    else:
        print(f"  [FAIL] MainWindow.qml not found at {main_file}")
        sys.exit(1)
except Exception as e:
    print(f"  [FAIL] File check error: {e}")
    sys.exit(1)

# Step 6: Check JarvisBridge import
print("\n[STEP 6] Checking JarvisBridge import...")
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from apps.desktop_ui.JarvisBridge import JarvisBridge, register_bridge
    print("  [OK] JarvisBridge imported")
except Exception as e:
    print(f"  [FAIL] JarvisBridge import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 7: Check TrayIcon import
print("\n[STEP 7] Checking TrayIcon import...")
try:
    from apps.desktop_ui.TrayIcon import TrayIcon
    print("  [OK] TrayIcon imported")
except Exception as e:
    print(f"  [FAIL] TrayIcon import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 8: Try creating QApplication
print("\n[STEP 8] Creating QApplication...")
try:
    app = QApplication(sys.argv)
    print("  [OK] QApplication created")
except Exception as e:
    print(f"  [FAIL] QApplication creation error: {e}")
    sys.exit(1)

# Step 9: Try creating QML engine
print("\n[STEP 9] Creating QML engine...")
try:
    engine = QQmlApplicationEngine()
    print("  [OK] QML engine created")
except Exception as e:
    print(f"  [FAIL] QML engine creation error: {e}")
    sys.exit(1)

# Step 10: Try registering bridge
print("\n[STEP 10] Registering bridge...")
try:
    register_bridge()
    print("  [OK] Bridge registered")
except Exception as e:
    print(f"  [FAIL] Bridge registration error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 11: Try creating bridge instance
print("\n[STEP 11] Creating bridge instance...")
try:
    bridge = JarvisBridge()
    print("  [OK] Bridge instance created")
except Exception as e:
    print(f"  [FAIL] Bridge instance creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 12: Try registering Theme singleton
print("\n[STEP 12] Registering Theme singleton...")
try:
    from PySide6.QtCore import QUrl
    ui_dir = Path(__file__).parent / "apps" / "desktop_ui"
    theme_path = ui_dir / "Theme.qml"
    qmlRegisterSingletonType(
        QUrl.fromLocalFile(str(theme_path)),
        "com.jarvis.theme",
        1, 0,
        "Theme"
    )
    print("  [OK] Theme singleton registered")
except Exception as e:
    print(f"  [FAIL] Theme registration error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 13: Try setting context property
print("\n[STEP 13] Setting context property...")
try:
    context = engine.rootContext()
    context.setContextProperty("jarvisBridge", bridge)
    print("  [OK] Context property set")
except Exception as e:
    print(f"  [FAIL] Context property error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 14: Try loading QML file
print("\n[STEP 14] Loading QML file...")
try:
    ui_dir = Path(__file__).parent / "apps" / "desktop_ui"
    qml_file = ui_dir / "MainWindow.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if engine.rootObjects():
        print("  [OK] QML file loaded successfully")
    else:
        print("  [FAIL] QML file loaded but no root objects")
        sys.exit(1)
except Exception as e:
    print(f"  [FAIL] QML loading error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All steps passed! UI should work.")
print("=" * 60)
print("\nTo launch UI, run:")
print("  python jarvis_ui.py")
print()

