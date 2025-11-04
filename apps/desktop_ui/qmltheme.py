"""
QML Theme Singleton Provider
Exposes Theme.qml as a singleton for use throughout the application.
"""

from PySide6.QtCore import QObject, Property
from PySide6.QtQml import qmlRegisterSingletonType, QmlElement

QML_IMPORT_NAME = "com.jarvis.theme"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Theme(QObject):
    """Theme singleton provider for QML."""
    
    def __init__(self, parent=None):
        super().__init__(parent)


def register_theme():
    """Register Theme.qml as a singleton."""
    from pathlib import Path
    from PySide6.QtQml import QQmlEngine, qmlRegisterSingletonType
    
    theme_path = Path(__file__).parent / "Theme.qml"
    qmlRegisterSingletonType(
        theme_path.as_uri(),
        QML_IMPORT_NAME,
        QML_IMPORT_MAJOR_VERSION,
        0,
        "Theme"
    )


