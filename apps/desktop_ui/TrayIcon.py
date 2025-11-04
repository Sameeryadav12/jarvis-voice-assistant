"""
System Tray Icon for Jarvis
Provides mini-orb icon, right-click menu, and quick access.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, Signal, QObject, Qt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TrayIcon(QObject):
    """System tray icon with menu and notifications."""
    
    # Signals
    show_window = Signal()
    hide_window = Signal()
    voice_trigger = Signal()
    quit_app = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available")
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_orb_icon())
        self.tray_icon.setToolTip("Jarvis Voice Assistant")
        
        # Create context menu
        self.menu = QMenu()
        self.setup_menu()
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show tray icon
        self.tray_icon.show()
        logger.info("System tray icon initialized")
    
    def create_orb_icon(self, size=16, state="idle"):
        """Create a mini orb icon for the system tray."""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Orb color based on state
        colors = {
            "idle": QColor(100, 108, 137),      # #647089 (muted)
            "listening": QColor(91, 140, 255),  # #5B8CFF (primary)
            "speaking": QColor(49, 238, 136),   # #31EE88 (success)
            "processing": QColor(245, 158, 11)  # #F59E0B (warning)
        }
        color = colors.get(state, colors["idle"])
        
        # Draw orb circle
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        
        # Add inner highlight
        painter.setBrush(QColor(255, 255, 255, 80))
        painter.drawEllipse(4, 4, (size - 8) // 2, (size - 8) // 2)
        
        painter.end()
        
        icon = QIcon(pixmap)
        return icon
    
    def setup_menu(self):
        """Setup the context menu."""
        # Show/Hide window
        show_action = self.menu.addAction("Show Jarvis")
        show_action.triggered.connect(self.show_window.emit)
        
        # Voice trigger
        voice_action = self.menu.addAction("🎤 Activate Voice")
        voice_action.triggered.connect(self.voice_trigger.emit)
        
        self.menu.addSeparator()
        
        # Recent activity
        recent_action = self.menu.addAction("📋 Recent Activity")
        # TODO: Connect to activity view
        
        # Settings
        settings_action = self.menu.addAction("⚙️ Settings")
        # TODO: Connect to settings window
        
        self.menu.addSeparator()
        
        # Quit
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app.emit)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - could show menu or toggle window
            pass
    
    def update_state(self, state="idle"):
        """Update the tray icon based on current state."""
        self.tray_icon.setIcon(self.create_orb_icon(state=state))
    
    def show_notification(self, title, message, duration=3000):
        """Show a system tray notification."""
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            duration
        )
    
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, duration=3000):
        """Show a message in the system tray."""
        self.tray_icon.showMessage(title, message, icon, duration)

