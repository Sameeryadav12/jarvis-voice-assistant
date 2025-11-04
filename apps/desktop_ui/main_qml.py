"""
Jarvis Desktop UI - QML Version
Modern QML-based interface with voice orb, transcript ticker, and activity cards.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
from PySide6.QtCore import QUrl, QObject
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.desktop_ui.JarvisBridge import JarvisBridge, register_bridge
from apps.desktop_ui.TrayIcon import TrayIcon

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for QML-based UI."""
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis")
    app.setOrganizationName("Jarvis")
    
    # Ensure system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        logger.warning("System tray is not available")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Register Python types
    register_bridge()
    
    # Create bridge instance
    bridge = JarvisBridge()
    
    # Register Theme singleton
    theme_path = Path(__file__).parent / "Theme.qml"
    qmlRegisterSingletonType(
        QUrl.fromLocalFile(str(theme_path)),
        "com.jarvis.theme",
        1, 0,
        "Theme"
    )
    
    # Register bridge as context property
    context = engine.rootContext()
    context.setContextProperty("jarvisBridge", bridge)
    
    # Load main QML file
    qml_file = Path(__file__).parent / "MainWindow.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        logger.error("Failed to load QML")
        sys.exit(-1)
    
    # Create system tray
    tray = TrayIcon()
    tray.show_window.connect(lambda: engine.rootObjects()[0].show())
    tray.voice_trigger.connect(bridge.activateVoice)
    tray.quit_app.connect(app.quit)
    
    # Note: Properties are automatically bound via context property
    # QML will access jarvisBridge.audioAmplitude, jarvisBridge.orbState, etc.
    
    logger.info("Jarvis QML UI started")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

