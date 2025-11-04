"""
Jarvis 2.0 - Neo-Futuristic Calm UI
Complete redesign with modern glass-inspired interface
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFrame, QGridLayout, QScrollArea,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSize, Property, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QFont, QPalette, QColor, QLinearGradient, QPainter,
    QBrush, QPen, QPixmap, QPaintEvent
)
import math
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
from core.nlu.router import CommandRouter

# Audio imports for voice input and output
try:
    import sounddevice as sd
    import numpy as np
    from core.audio.stt_faster_whisper import FasterWhisperSTT, create_faster_whisper
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from simple_tts import SimpleTTS
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    logger.warning(f"Voice input not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# COLOR SYSTEM - Neo-Futuristic Calm Palette
# ============================================================================

class NeoColors:
    """Design system colors from spec."""
    
    # Backgrounds
    BACKGROUND_MAIN = "#0B0F1A"         # Deep navy-black
    SURFACE = "#111827"                 # Elevated elements
    GLASS_OVERLAY = "rgba(255,255,255,0.06)"  # Transparent glass
    
    # Accents
    ACCENT_PRIMARY = "#2563EB"          # Primary blue
    ACCENT_SECONDARY = "#14B8A6"        # Cyan-teal
    ACCENT_PURPLE = "#9333EA"           # Purple accent
    
    # Text
    TEXT_PRIMARY = "#F9FAFB"            # Pure white
    TEXT_SECONDARY = "#CBD5E1"          # Gray subtext
    TEXT_CAPTION = "#A8B2C7"            # Caption gray
    
    # Borders
    DIVIDER = "#334155"                 # Section separators
    
    # States
    DANGER = "#F43F5E"                  # Stop/Error
    SUCCESS = "#22C55E"                 # Ready/Connected
    WARNING = "#FACC15"                 # Notifications
    
    # Status colors
    STATUS_READY = "#22C55E"            # Green
    STATUS_LISTENING = "#14B8A6"        # Cyan
    STATUS_THINKING = "#FACC15"         # Amber
    STATUS_SPEAKING = "#3B82F6"         # Blue


class NeoFonts:
    """Typography system."""
    
    @staticmethod
    def get_font(size=14, weight=400):
        """Get Inter font with specified size and weight."""
        font = QFont("Inter", size)
        if weight == 300:
            font.setWeight(QFont.Light)
        elif weight == 400:
            font.setWeight(QFont.Normal)
        elif weight == 600:
            font.setWeight(QFont.DemiBold)
        elif weight == 700:
            font.setWeight(QFont.Bold)
        font.setLetterSpacing(QFont.PercentageSpacing, 101)  # +1% spacing
        return font
    
    @staticmethod
    def title():
        """App title font - 24px, bold."""
        font = QFont("Inter", 24)
        font.setWeight(QFont.Bold)
        font.setLetterSpacing(QFont.PercentageSpacing, 102)
        return font
    
    @staticmethod
    def section_title():
        """Section titles - 15px, semi-bold."""
        return NeoFonts.get_font(15, 600)
    
    @staticmethod
    def body():
        """Body text - 13px, normal."""
        return NeoFonts.get_font(13, 400)
    
    @staticmethod
    def caption():
        """Caption text - 11px, light."""
        return NeoFonts.get_font(11, 300)


# ============================================================================
# ANIMATED VOICE ORB
# ============================================================================

class VoiceOrb(QWidget):
    """Animated voice orb with gradient and glow effects for all states."""
    
    # State-based colors from storyboard
    STATE_COLORS = {
        "idle": ("#2563EB", "#14B8A6"),      # Blue → Cyan
        "listening": ("#14B8A6", "#0EA5E9"), # Cyan-teal → Cyan
        "processing": ("#FACC15", "#2563EB"),# Amber → Blue
        "speaking": ("#FFFFFF", "#93C5FD"),  # White → Light blue
        "error": ("#F43F5E", "#7F1D1D")      # Red → Dark red
    }
    
    STATE_SIZES = {
        "idle": 120,
        "listening": 150,
        "processing": 140,
        "speaking": 160,
        "error": 120
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)  # Compact canvas
        
        # Animation state
        self._scale = 1.0
        self._glow_opacity = 0.7
        self._rotation = 0.0
        self._ripple_phase = 0.0
        self.state = "idle"
        self.target_size = 120
        self.current_size = 120
        
        # Initialize timers
        self.rotation_timer = None
        self.ripple_timer = None
        
        # Setup animations
        self.setup_animations()
    
    def setup_animations(self):
        """Setup breathing and pulse animations."""
        # Breathing animation (idle state)
        self.breathing_anim = QPropertyAnimation(self, b"glow_opacity")
        self.breathing_anim.setDuration(2000)
        self.breathing_anim.setStartValue(0.9)
        self.breathing_anim.setEndValue(0.6)
        self.breathing_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.breathing_anim.setLoopCount(-1)  # Infinite
        
        # Pulse animation (listening state)
        self.pulse_anim = QPropertyAnimation(self, b"scale")
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setStartValue(1.0)
        self.pulse_anim.setEndValue(1.1)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.pulse_anim.setLoopCount(-1)
    
    def get_glow_opacity(self):
        return self._glow_opacity
    
    def set_glow_opacity(self, value):
        self._glow_opacity = value
        self.update()
    
    glow_opacity = Property(float, get_glow_opacity, set_glow_opacity)
    
    def get_scale(self):
        return self._scale
    
    def set_scale(self, value):
        self._scale = value
        self.update()
    
    scale = Property(float, get_scale, set_scale)
    
    def setState(self, state):
        """Change orb state and update animations."""
        self.state = state
        
        # Stop all animations and timers
        self.breathing_anim.stop()
        self.pulse_anim.stop()
        
        # Stop rotation and ripple timers if they exist
        if hasattr(self, 'rotation_timer') and self.rotation_timer:
            self.rotation_timer.stop()
        if hasattr(self, 'ripple_timer') and self.ripple_timer:
            self.ripple_timer.stop()
        
        if state == "idle":
            self.breathing_anim.start()
        elif state == "listening":
            self.pulse_anim.start()
        elif state == "processing":
            self._start_processing_animation()
        elif state == "speaking":
            self._start_speaking_animation()
        
        self.update()
    
    def _start_idle_animation(self):
        """Idle breathing animation."""
        # Already handled by breathing_anim
        pass
    
    def _start_processing_animation(self):
        """Rotating ring animation for processing."""
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self._update_rotation)
        self.rotation_timer.start(30)  # 33 FPS
    
    def _update_rotation(self):
        """Update rotation angle."""
        self._rotation = (self._rotation + 3) % 360
        self.update()
    
    def _start_speaking_animation(self):
        """Ripple animation for speaking."""
        self.ripple_timer = QTimer()
        self.ripple_timer.timeout.connect(self._update_ripple)
        self.ripple_timer.start(50)  # 20 FPS
    
    def _update_ripple(self):
        """Update ripple phase."""
        self._ripple_phase = (self._ripple_phase + 0.1) % 2.0
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """Draw the orb with gradient and glow based on state."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPoint(90, 90)  # Center of 180x180 canvas
        
        # Get state colors
        color1, color2 = self.STATE_COLORS.get(self.state, self.STATE_COLORS["idle"])
        base_radius = self.STATE_SIZES.get(self.state, 150) // 2
        radius = int(base_radius * self._scale)
        
        # Draw ripples for speaking state
        if self.state == "speaking":
            for i in range(3):
                ripple_radius = radius + 20 + (i * 15) + int(self._ripple_phase * 10)
                ripple_opacity = (0.3 - i * 0.1) * self._glow_opacity
                painter.setOpacity(ripple_opacity)
                painter.setBrush(Qt.NoBrush)
                pen = QPen(QColor(color1))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawEllipse(center, ripple_radius, ripple_radius)
        
        # Draw outer glow
        glow_gradient = QLinearGradient(center.x() - radius, center.y() - radius,
                                        center.x() + radius, center.y() + radius)
        glow_gradient.setColorAt(0, QColor(color1))
        glow_gradient.setColorAt(1, QColor(color2))
        
        painter.setOpacity(self._glow_opacity * 0.3)
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius + 30, radius + 30)
        
        # Draw main orb with gradient
        painter.setOpacity(1.0)
        orb_gradient = QLinearGradient(center.x() - radius, center.y() - radius,
                                       center.x() + radius, center.y() + radius)
        orb_gradient.setColorAt(0, QColor(color1))
        orb_gradient.setColorAt(1, QColor(color2))
        
        painter.setBrush(QBrush(orb_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        # Draw rotating ring for processing state
        if self.state == "processing":
            painter.setOpacity(0.7)
            pen = QPen(QColor(color2))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            # Draw arc that rotates
            start_angle = int(self._rotation * 16)
            span_angle = 120 * 16
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, start_angle, span_angle)
        
        # Draw inner highlight (except for speaking state)
        if self.state != "speaking":
            painter.setOpacity(0.4)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            highlight_size = radius // 2
            painter.drawEllipse(center.x() - radius//3, center.y() - radius//2,
                              highlight_size, highlight_size)


# ============================================================================
# GRADIENT BUTTON
# ============================================================================

class GradientButton(QPushButton):
    """Button with gradient background and hover effects."""
    
    def __init__(self, text, color1, color2, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text} {text}" if icon_text else text)
        self.color1 = QColor(color1)
        self.color2 = QColor(color2)
        self.is_hovered = False
        
        # Styling
        self.setMinimumSize(200, 42)
        self.setFont(NeoFonts.get_font(13, 600))
        self.setCursor(Qt.PointingHandCursor)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(self.color1.red(), self.color1.green(), 
                              self.color1.blue(), 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2}
                );
                color: {NeoColors.TEXT_PRIMARY};
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._brighten(color1)}, 
                    stop:1 {self._brighten(color2)}
                );
            }}
            QPushButton:pressed {{
                padding-top: 12px;
                padding-bottom: 8px;
            }}
        """)
    
    def _brighten(self, hex_color):
        """Brighten color by 3%."""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        v = min(255, int(v * 1.03))
        color.setHsv(h, s, v, a)
        return color.name()


# ============================================================================
# QUICK ACTION CARD
# ============================================================================

class QuickActionCard(QFrame):
    """Glass-style quick action card with icon and text."""
    
    clicked = Signal(str)
    
    def __init__(self, icon, title, hint, command, parent=None):
        super().__init__(parent)
        self.command = command
        self.is_hovered = False
        
        self.setFixedSize(240, 65)
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(NeoFonts.get_font(13, 600))
        title_label.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY};")
        text_layout.addWidget(title_label)
        
        hint_label = QLabel(hint)
        hint_label.setFont(NeoFonts.get_font(10, 300))
        hint_label.setStyleSheet(f"color: {NeoColors.TEXT_CAPTION};")
        text_layout.addWidget(hint_label)
        
        layout.addLayout(text_layout)
        self.setLayout(layout)
        
        # Base style
        self.update_style()
    
    def update_style(self):
        """Update card styling based on hover state."""
        border = f"1px solid {NeoColors.ACCENT_SECONDARY}" if self.is_hovered else "none"
        bg_color = "rgba(255,255,255,0.09)" if self.is_hovered else "rgba(255,255,255,0.06)"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: {border};
                border-radius: 20px;
            }}
        """)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        self.is_hovered = True
        self.update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self.is_hovered = False
        self.update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.command)
        super().mousePressEvent(event)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class JarvisNeoUI(QMainWindow):
    """Jarvis 2.0 - Neo-Futuristic Calm UI."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize backend
        logger.info("Initializing Jarvis 2.0 backend...")
        self.init_backend()
        
        # Setup UI
        logger.info("Building Neo-Futuristic UI...")
        self.init_ui()
        
        logger.info("Jarvis 2.0 ready!")
    
    def init_backend(self):
        """Initialize NLU and skills."""
        self.classifier = IntentClassifier()
        self.router = CommandRouter()
        self.info_skills = InformationSkills()
        self.system_skills = SystemSkills()
        self.reminder_skills = ReminderSkills()
        
        # Register handlers
        for intent_type in [IntentType.GET_TIME, IntentType.GET_DATE, 
                           IntentType.GET_BATTERY, IntentType.GET_SYSTEM_INFO, 
                           IntentType.HELP]:
            self.router.register_handler(intent_type, self.info_skills.handle_intent)
        
        for intent_type in [IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, 
                           IntentType.VOLUME_SET, IntentType.MUTE, IntentType.UNMUTE]:
            self.router.register_handler(intent_type, self.system_skills.handle_intent)
        
        for intent_type in [IntentType.SET_TIMER, IntentType.LIST_REMINDERS]:
            self.router.register_handler(intent_type, self.reminder_skills.handle_intent)
        
        # Initialize voice input if available
        self.stt = None
        self.tts = None
        self.is_recording = False
        self.audio_buffer = []
        
        if VOICE_AVAILABLE:
            try:
                # Initialize STT (Speech-to-Text)
                logger.info("Initializing Faster Whisper STT...")
                self.stt = create_faster_whisper(model_size="tiny", device="cpu")
                if self.stt:
                    logger.info("✅ Voice input ready!")
                else:
                    logger.warning("Failed to create STT instance")
                
                # Initialize TTS (Text-to-Speech)
                logger.info("Initializing Simple TTS...")
                self.tts = SimpleTTS(voice="en-US-AriaNeural")
                logger.info("✅ Voice output ready!")
                    
            except Exception as e:
                logger.error(f"Voice initialization failed: {e}")
                self.stt = None
                self.tts = None
        
        self.current_status = "ready"
    
    def init_ui(self):
        """Build the complete UI."""
        self.setWindowTitle("Jarvis 2.0 - Neo-Futuristic")
        self.setGeometry(100, 50, 1440, 900)
        self.setMinimumSize(1400, 900)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 2, 50, 2)
        main_layout.setSpacing(6)
        central_widget.setLayout(main_layout)
        
        # Apply background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {NeoColors.BACKGROUND_MAIN};
            }}
            QWidget {{
                background-color: {NeoColors.BACKGROUND_MAIN};
                color: {NeoColors.TEXT_PRIMARY};
            }}
        """)
        
        # Build sections
        self.build_header(main_layout)
        self.build_hero_section(main_layout)
        self.build_action_bar(main_layout)
        self.build_quick_actions(main_layout)
        self.build_conversation_panel(main_layout)
        self.build_footer(main_layout)
    
    def build_header(self, parent_layout):
        """Build header bar with logo and status."""
        header = QFrame()
        header.setFixedHeight(55)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(17, 24, 39, 0.8);
                border-bottom: 1px solid {NeoColors.DIVIDER};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        header.setLayout(layout)
        
        # Left: Logo + Title
        left_layout = QHBoxLayout()
        logo = QLabel("🤖")
        logo.setFont(QFont("Segoe UI Emoji", 20))
        left_layout.addWidget(logo)
        
        title = QLabel("Jarvis")
        title.setFont(NeoFonts.title())
        title.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY};")
        left_layout.addWidget(title)
        left_layout.addStretch()
        
        layout.addLayout(left_layout)
        
        # Center: Status
        self.status_label = QLabel("● Ready")
        self.status_label.setFont(NeoFonts.get_font(14, 600))
        self.status_label.setStyleSheet(f"color: {NeoColors.STATUS_READY};")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Right: Controls
        right_layout = QHBoxLayout()
        right_layout.addStretch()
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFont(QFont("Segoe UI Emoji", 16))
        settings_btn.setFixedSize(35, 35)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        settings_btn.setCursor(Qt.PointingHandCursor)
        right_layout.addWidget(settings_btn)
        
        help_btn = QPushButton("❔")
        help_btn.setFont(QFont("Segoe UI Emoji", 16))
        help_btn.setFixedSize(35, 35)
        help_btn.setStyleSheet(settings_btn.styleSheet())
        help_btn.setCursor(Qt.PointingHandCursor)
        right_layout.addWidget(help_btn)
        
        layout.addLayout(right_layout)
        
        parent_layout.addWidget(header)
    
    def build_hero_section(self, parent_layout):
        """Build hero section with voice orb and transcript."""
        hero = QWidget()
        hero.setMinimumHeight(220)
        hero.setMaximumHeight(240)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 8, 15, 10)
        hero.setLayout(layout)
        
        # Voice Orb
        self.voice_orb = VoiceOrb()
        self.voice_orb.setState("idle")
        layout.addWidget(self.voice_orb, alignment=Qt.AlignCenter)
        
        # Transcript
        self.transcript_label = QLabel("Say something like 'What's the weather today?'")
        self.transcript_label.setFont(NeoFonts.get_font(13, 400))
        self.transcript_label.setStyleSheet(f"color: {NeoColors.TEXT_SECONDARY}; padding: 12px; margin-bottom: 10px;")
        self.transcript_label.setAlignment(Qt.AlignCenter)
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setMaximumWidth(700)
        self.transcript_label.setMinimumHeight(35)
        layout.addWidget(self.transcript_label)
        
        parent_layout.addWidget(hero)
    
    def build_action_bar(self, parent_layout):
        """Build text input field and action buttons."""
        # Container for input and buttons
        action_container = QWidget()
        action_container.setMinimumHeight(95)
        action_container.setMaximumHeight(105)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(8)
        container_layout.setContentsMargins(50, 6, 50, 6)
        action_container.setLayout(container_layout)
        
        # Text input field
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_widget.setLayout(input_layout)
        
        input_label = QLabel("💬 Type:")
        input_label.setFont(NeoFonts.get_font(12, 600))
        input_label.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY};")
        input_layout.addWidget(input_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., 'what time is it', 'check battery', 'set volume to 50'")
        self.command_input.setFont(NeoFonts.get_font(12, 400))
        self.command_input.setMinimumHeight(35)
        self.command_input.setMaximumHeight(35)
        self.command_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {NeoColors.SURFACE};
                color: {NeoColors.TEXT_PRIMARY};
                border: 2px solid {NeoColors.DIVIDER};
                border-radius: 22px;
                padding: 0 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {NeoColors.ACCENT_SECONDARY};
            }}
        """)
        self.command_input.returnPressed.connect(self.process_text_from_input)
        input_layout.addWidget(self.command_input)
        
        container_layout.addWidget(input_widget)
        
        # Buttons row
        action_bar = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(50)
        layout.setContentsMargins(0, 0, 0, 0)
        action_bar.setLayout(layout)
        
        layout.addStretch()
        
        # Start Listening button (enabled if voice available)
        self.listen_btn = GradientButton(
            "Start Listening",
            NeoColors.ACCENT_PRIMARY if VOICE_AVAILABLE else "#6B7280",
            NeoColors.ACCENT_SECONDARY if VOICE_AVAILABLE else "#4B5563",
            "🎙️"
        )
        self.listen_btn.setMinimumWidth(200)
        self.listen_btn.setMaximumWidth(210)
        self.listen_btn.clicked.connect(self.start_voice_listening)
        if not VOICE_AVAILABLE:
            self.listen_btn.setEnabled(False)
            self.listen_btn.setToolTip("Voice input initializing...")
        layout.addWidget(self.listen_btn)
        
        # Process Text button
        self.process_btn = GradientButton(
            "Send Command",
            "#3B82F6",
            NeoColors.ACCENT_PURPLE,
            "🚀"
        )
        self.process_btn.setMinimumWidth(190)
        self.process_btn.setMaximumWidth(200)
        self.process_btn.clicked.connect(self.process_text_from_input)
        layout.addWidget(self.process_btn)
        
        layout.addStretch()
        
        container_layout.addWidget(action_bar)
        parent_layout.addWidget(action_container)
    
    def build_quick_actions(self, parent_layout):
        """Build quick action grid."""
        container = QWidget()
        container.setMinimumHeight(150)
        container.setMaximumHeight(160)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 5, 0, 5)
        container.setLayout(layout)
        
        # Title
        title = QLabel("Quick Actions")
        title.setFont(NeoFonts.section_title())
        title.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY}; padding-bottom: 3px;")
        layout.addWidget(title)
        
        # Grid container with centered alignment
        grid_container = QWidget()
        grid_container_layout = QHBoxLayout()
        grid_container_layout.setAlignment(Qt.AlignCenter)
        grid_container.setLayout(grid_container_layout)
        
        grid_widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)
        grid_widget.setLayout(grid)
        
        actions = [
            ("📅", "Calendar", "Check schedule", "show calendar"),
            ("⏰", "Reminders", "Set reminder", "list reminders"),
            ("🔊", "Volume", "Control audio", "get volume"),
            ("🌐", "Search", "Web search", "search the web"),
            ("📝", "Notes", "Quick note", "take a note"),
            ("💻", "System", "System info", "show system status"),
        ]
        
        # Place in 2 rows x 3 columns
        for i, (icon, title_text, hint, command) in enumerate(actions):
            card = QuickActionCard(icon, title_text, hint, command)
            card.clicked.connect(self.quick_action)
            row = i // 3  # Row 0 for first 3, Row 1 for last 3
            col = i % 3   # Col 0, 1, 2
            grid.addWidget(card, row, col, Qt.AlignCenter)
        
        grid_container_layout.addWidget(grid_widget)
        
        layout.addWidget(grid_container)
        parent_layout.addWidget(container)
    
    def build_conversation_panel(self, parent_layout):
        """Build conversation history panel."""
        container = QWidget()
        container.setMinimumHeight(110)
        container.setMaximumHeight(125)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 5, 0, 5)
        container.setLayout(layout)
        
        # Title
        title = QLabel("Conversation")
        title.setFont(NeoFonts.section_title())
        title.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY}; padding-bottom: 3px;")
        layout.addWidget(title)
        
        # Scroll area for messages
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(85)
        scroll.setMaximumHeight(100)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0F172A, stop:1 #1E293B
                );
                border: none;
                border-radius: 20px;
                padding: 8px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {NeoColors.DIVIDER};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {NeoColors.ACCENT_SECONDARY};
            }}
        """)
        
        self.conversation_widget = QWidget()
        self.conversation_layout = QVBoxLayout()
        self.conversation_layout.setAlignment(Qt.AlignTop)
        self.conversation_layout.setSpacing(8)
        self.conversation_layout.setContentsMargins(8, 8, 8, 8)
        self.conversation_widget.setLayout(self.conversation_layout)
        
        scroll.setWidget(self.conversation_widget)
        layout.addWidget(scroll)
        
        # Add welcome message
        self.add_message("jarvis", "Hello! I'm Jarvis 2.0. How can I help you today?")
        
        parent_layout.addWidget(container)
    
    def build_footer(self, parent_layout):
        """Build footer bar."""
        footer = QFrame()
        footer.setFixedHeight(35)
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(17, 24, 39, 0.9);
                border-top: 1px solid {NeoColors.DIVIDER};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        footer.setLayout(layout)
        
        # Left: Connection status
        conn_label = QLabel("● Connected to voice engine")
        conn_label.setFont(NeoFonts.caption())
        conn_label.setStyleSheet(f"color: {NeoColors.STATUS_READY};")
        layout.addWidget(conn_label)
        
        layout.addStretch()
        
        # Center: CPU (placeholder)
        cpu_label = QLabel("CPU: 12%")
        cpu_label.setFont(NeoFonts.caption())
        cpu_label.setStyleSheet(f"color: {NeoColors.TEXT_CAPTION};")
        layout.addWidget(cpu_label)
        
        layout.addStretch()
        
        # Right: Offline mode toggle
        offline_label = QLabel("Offline mode: OFF")
        offline_label.setFont(NeoFonts.caption())
        offline_label.setStyleSheet(f"color: {NeoColors.TEXT_CAPTION};")
        layout.addWidget(offline_label)
        
        parent_layout.addWidget(footer)
    
    def add_message(self, sender, text):
        """Add a message to conversation panel."""
        # Create container for proper alignment
        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container.setLayout(container_layout)
        
        message = QFrame()
        message.setMaximumWidth(550)  # Limit message width
        message_layout = QHBoxLayout()
        message_layout.setContentsMargins(12, 8, 12, 8)
        message.setLayout(message_layout)
        
        label = QLabel(text)
        label.setFont(NeoFonts.get_font(12, 400))
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {NeoColors.TEXT_PRIMARY};")
        message_layout.addWidget(label)
        
        if sender == "user":
            container_layout.addStretch()
            container_layout.addWidget(message)
            message.setStyleSheet(f"""
                QFrame {{
                    background-color: #1E3A8A;
                    border-radius: 15px;
                }}
            """)
        else:  # jarvis
            container_layout.addWidget(message)
            container_layout.addStretch()
            message.setStyleSheet(f"""
                QFrame {{
                    background-color: {NeoColors.SURFACE};
                    border-radius: 15px;
                }}
            """)
        
        self.conversation_layout.addWidget(container)
    
    def set_status(self, status, text):
        """Update status indicator and orb state."""
        self.current_status = status
        
        # Map status to colors
        colors = {
            "idle": NeoColors.STATUS_READY,
            "ready": NeoColors.STATUS_READY,
            "listening": NeoColors.STATUS_LISTENING,
            "processing": NeoColors.STATUS_THINKING,
            "thinking": NeoColors.STATUS_THINKING,
            "speaking": NeoColors.STATUS_SPEAKING,
        }
        
        # Map status to orb states
        orb_states = {
            "idle": "idle",
            "ready": "idle",
            "listening": "listening",
            "processing": "processing",
            "thinking": "processing",
            "speaking": "speaking",
        }
        
        self.status_label.setText(f"● {text}")
        self.status_label.setStyleSheet(f"color: {colors.get(status, NeoColors.TEXT_PRIMARY)};")
        self.voice_orb.setState(orb_states.get(status, "idle"))
    
    def start_voice_listening(self):
        """Start voice listening - PHASE 2 IMPLEMENTATION."""
        if not VOICE_AVAILABLE or not self.stt:
            self.add_message("jarvis", "Voice input not available. Please check microphone.")
            return
        
        if self.is_recording:
            # Stop recording
            self.stop_voice_recording()
        else:
            # Start recording
            self.is_recording = True
            self.audio_buffer = []
            
            # Update UI
            self.set_status("listening", "Listening...")
            self.transcript_label.setText("🎙️ Speak now... (will stop in 5 seconds)")
            self.listen_btn.setText("🔴 Stop Recording")
            
            # Record for 5 seconds
            try:
                sample_rate = 16000
                duration = 5  # seconds
                
                logger.info(f"Starting audio recording ({duration}s)...")
                
                # Record in background thread
                def record_audio():
                    try:
                        audio_data = sd.rec(
                            int(sample_rate * duration),
                            samplerate=sample_rate,
                            channels=1,
                            dtype='float32'
                        )
                        sd.wait()  # Wait for recording to finish
                        
                        # Process on main thread
                        QTimer.singleShot(0, lambda: self._process_voice_input(audio_data[:, 0], sample_rate))
                    except Exception as e:
                        logger.error(f"Recording error: {e}")
                        QTimer.singleShot(0, lambda: self._voice_error(str(e)))
                
                import threading
                threading.Thread(target=record_audio, daemon=True).start()
                
            except Exception as e:
                logger.error(f"Failed to start recording: {e}")
                self._voice_error(str(e))
    
    def stop_voice_recording(self):
        """Stop voice recording early."""
        if self.is_recording:
            sd.stop()
            self.is_recording = False
            self.listen_btn.setText("🎙️ Start Listening")
            self.set_status("ready", "Ready")
            self.transcript_label.setText("Recording stopped")
    
    def _process_voice_input(self, audio_data, sample_rate):
        """Process recorded voice input."""
        try:
            self.is_recording = False
            self.listen_btn.setText("🎙️ Start Listening")
            
            # Update to processing state
            self.set_status("processing", "Processing speech...")
            self.transcript_label.setText("🧠 Transcribing your speech...")
            
            # Transcribe in background
            def transcribe():
                try:
                    logger.info("Transcribing audio...")
                    transcript = self.stt.transcribe(audio_data, sample_rate)
                    
                    # Clean up transcript
                    if transcript:
                        transcript = transcript.strip()
                    
                    if transcript and len(transcript) > 2:
                        logger.info(f"✅ Transcript: {transcript}")
                        # Update UI on main thread
                        QTimer.singleShot(0, lambda: self._on_transcript_ready(transcript))
                    else:
                        logger.warning("No speech detected in audio")
                        # Show apology message
                        QTimer.singleShot(0, lambda: self._no_speech_detected())
                except Exception as e:
                    logger.error(f"Transcription error: {e}")
                    QTimer.singleShot(0, lambda: self._voice_error(str(e)))
            
            import threading
            threading.Thread(target=transcribe, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            self._voice_error(str(e))
    
    def _on_transcript_ready(self, transcript):
        """Handle completed transcript."""
        # Show what was heard
        self.transcript_label.setText(f'✅ You said: "{transcript}"')
        self.command_input.setText(transcript)
        
        # Add to conversation
        self.add_message("user", transcript)
        
        # Process the command after short delay
        logger.info(f"Processing voice command: {transcript}")
        QTimer.singleShot(800, lambda: self._process_command(transcript))
    
    def _no_speech_detected(self):
        """Handle no speech detected."""
        self.set_status("ready", "Ready")
        self.transcript_label.setText("⚠️ I didn't catch that. Please try again.")
        
        apology = "I'm sorry, I didn't hear anything. Please try speaking again."
        self.add_message("jarvis", apology)
        
        # Speak apology if TTS available
        if self.tts:
            def speak_apology():
                try:
                    self.tts.speak(apology)
                except Exception as e:
                    logger.error(f"TTS error in apology: {e}")
            
            import threading
            threading.Thread(target=speak_apology, daemon=True).start()
    
    def _voice_error(self, error_msg):
        """Handle voice input error."""
        self.is_recording = False
        self.listen_btn.setText("🎙️ Start Listening")
        self.set_status("ready", "Ready")
        self.transcript_label.setText(f"⚠️ Error: {error_msg}")
        
        error_response = f"Sorry, I encountered an error: {error_msg}"
        self.add_message("jarvis", error_response)
        
        # Speak error message
        if self.tts:
            def speak_error():
                try:
                    self.tts.speak("Sorry, I encountered an error with voice input.")
                except:
                    pass
            
            import threading
            threading.Thread(target=speak_error, daemon=True).start()
    
    def process_text_from_input(self):
        """Process command from input field."""
        command = self.command_input.text().strip()
        
        if not command:
            self.transcript_label.setText("⚠️ Please type a command first!")
            return
        
        # Clear input field
        self.command_input.clear()
        
        # Update UI
        self.set_status("thinking", "Thinking...")
        self.transcript_label.setText(f"Processing: {command}")
        self.add_message("user", command)
        
        # Process command
        QTimer.singleShot(500, lambda: self._process_command(command))
    
    def _process_command(self, command):
        """Actually process the command."""
        try:
            import asyncio
            
            # Processing state with amber orb and rotating ring
            self.set_status("processing", "Processing...")
            self.transcript_label.setText(f"🧠 Analyzing: {command}")
            
            # Process command
            intent = self.classifier.classify(command)
            result = asyncio.run(self.router.route(intent))
            
            # Speaking state with white ripple orb
            self.set_status("speaking", "Speaking...")
            self.transcript_label.setText(f"💬 {result.message[:60]}...")
            self.add_message("jarvis", result.message)
            
            # Speak the response if TTS available
            if self.tts and result.message:
                logger.info(f"🔊 Speaking: {result.message[:50]}...")
                
                # Speak in background thread to not block UI
                def speak_response():
                    try:
                        success = self.tts.speak(result.message)
                        if success:
                            logger.info("✅ TTS playback complete")
                        else:
                            logger.warning("TTS playback failed")
                    except Exception as e:
                        logger.error(f"TTS error: {e}")
                    finally:
                        # Return to ready on main thread
                        QTimer.singleShot(0, self._return_to_ready)
                
                import threading
                threading.Thread(target=speak_response, daemon=True).start()
            else:
                # No TTS - return to ready after short delay
                logger.warning("TTS not available")
                QTimer.singleShot(2000, self._return_to_ready)
                
        except Exception as e:
            self.add_message("jarvis", f"Error: {str(e)}")
            self.set_status("error", "Error")
            QTimer.singleShot(2000, lambda: self.set_status("ready", "Ready"))
    
    def _return_to_ready(self):
        """Return UI to ready state."""
        self.set_status("ready", "Ready")
        self.transcript_label.setText("Say something like 'What's the weather today?'")
    
    def quick_action(self, command):
        """Handle quick action click."""
        self.add_message("user", command)
        self.set_status("thinking", "Processing...")
        QTimer.singleShot(500, lambda: self._process_command(command))
    
    def closeEvent(self, event):
        """Handle window close."""
        self.reminder_skills.shutdown()
        event.accept()


def main():
    """Launch Jarvis 2.0."""
    logger.info("🚀 Starting Jarvis 2.0 - Neo-Futuristic UI...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis 2.0")
    
    # Set Inter font if available, fallback to system
    app.setFont(NeoFonts.body())
    
    window = JarvisNeoUI()
    window.show()
    
    logger.info("✨ Jarvis 2.0 UI launched successfully!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

