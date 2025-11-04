#!/usr/bin/env python3
"""
Jarvis Desktop UI Application
Launch the PySide6 desktop interface (QML version).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Try QML version first, fallback to widgets
try:
    from apps.desktop_ui.main_qml import main
except ImportError as e:
    print(f"Warning: QML UI not available ({e}), using widget-based UI")
    from PySide6.QtWidgets import QApplication
    from apps.desktop_ui.main_window import JarvisMainWindow
    
    def main():
        """Main entry point (widget fallback)."""
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = JarvisMainWindow()
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()



