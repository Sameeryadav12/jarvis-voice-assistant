"""
Jarvis Modern UI - Completely Redesigned
Clean, professional, eye-catching interface with perfect spacing
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QTextBrowser,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QFont, QColor, QLinearGradient, QPainter, QBrush, QPen, QPaintEvent
import logging

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
from core.nlu.router import CommandRouter

# Voice imports
try:
    import sounddevice as sd
    import numpy as np
    from core.audio.stt_faster_whisper import create_faster_whisper
    from simple_tts import SimpleTTS
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    logging.warning(f"Voice unavailable: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MODERN COLOR PALETTE - Professional & Eye-Catching
# ============================================================================

class ModernColors:
    """Clean modern color system."""
    
    # Background - Deep dark with subtle gradient
    BG_DARK = "#0A0E27"
    BG_CARD = "#121935"
    
    # Primary brand - Electric Blue
    PRIMARY = "#3B82F6"
    PRIMARY_LIGHT = "#60A5FA"
    PRIMARY_DARK = "#2563EB"
    
    # Accent - Cyan
    ACCENT = "#06B6D4"
    ACCENT_LIGHT = "#22D3EE"
    
    # Success/Ready
    SUCCESS = "#10B981"
    
    # Warning/Processing
    WARNING = "#F59E0B"
    
    # Text
    TEXT_PRIMARY = "#F9FAFB"
    TEXT_SECONDARY = "#9CA3AF"
    TEXT_MUTED = "#6B7280"
    
    # Border
    BORDER = "#1F2937"
    BORDER_LIGHT = "#374151"


# ============================================================================
# COMPACT MODERN ORB - Clean & Simple
# ============================================================================

class ModernOrb(QWidget):
    """Compact animated orb - clean design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 140)
        
        self._glow = 0.8
        self.state = "idle"
        
        # Breathing animation
        self.anim = QPropertyAnimation(self, b"glow")
        self.anim.setDuration(2000)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.5)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.setLoopCount(-1)
        self.anim.start()
    
    def get_glow(self):
        return self._glow
    
    def set_glow(self, value):
        self._glow = value
        self.update()
    
    glow = Property(float, get_glow, set_glow)
    
    def setState(self, state):
        """Change orb state."""
        self.state = state
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """Draw simple clean orb."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPoint(70, 70)
        radius = 50
        
        # State colors
        colors = {
            "idle": (ModernColors.PRIMARY, ModernColors.ACCENT),
            "listening": (ModernColors.ACCENT, ModernColors.ACCENT_LIGHT),
            "processing": (ModernColors.WARNING, ModernColors.PRIMARY),
            "speaking": ("#FFFFFF", ModernColors.PRIMARY_LIGHT),
        }
        
        color1, color2 = colors.get(self.state, colors["idle"])
        
        # Outer glow
        painter.setOpacity(self._glow * 0.3)
        gradient = QLinearGradient(0, 0, 140, 140)
        gradient.setColorAt(0, QColor(color1))
        gradient.setColorAt(1, QColor(color2))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius + 20, radius + 20)
        
        # Main orb
        painter.setOpacity(1.0)
        painter.drawEllipse(center, radius, radius)
        
        # Inner shine
        painter.setOpacity(0.3)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(center.x() - 15, center.y() - 20, 25, 25)


# ============================================================================
# MODERN MAIN WINDOW - Completely Redesigned
# ============================================================================

class JarvisModernUI(QMainWindow):
    """Modern Jarvis UI - Clean, Professional, No Overlaps."""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing Modern Jarvis UI...")
        self.init_backend()
        self.init_ui()
        logger.info("Modern UI ready!")
    
    def init_backend(self):
        """Initialize backend."""
        self.classifier = IntentClassifier()
        self.router = CommandRouter()
        self.info_skills = InformationSkills()
        self.system_skills = SystemSkills()
        self.reminder_skills = ReminderSkills()
        
        # Register handlers
        for intent in [IntentType.GET_TIME, IntentType.GET_DATE, 
                      IntentType.GET_BATTERY, IntentType.GET_SYSTEM_INFO, IntentType.HELP]:
            self.router.register_handler(intent, self.info_skills.handle_intent)
        
        for intent in [IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, 
                      IntentType.VOLUME_SET, IntentType.MUTE, IntentType.UNMUTE]:
            self.router.register_handler(intent, self.system_skills.handle_intent)
        
        for intent in [IntentType.SET_TIMER, IntentType.LIST_REMINDERS]:
            self.router.register_handler(intent, self.reminder_skills.handle_intent)
        
        # Voice setup
        self.stt = None
        self.tts = None
        self.is_recording = False
        
        if VOICE_AVAILABLE:
            try:
                self.stt = create_faster_whisper(model_size="tiny", device="cpu")
                self.tts = SimpleTTS(voice="en-US-AriaNeural")
                logger.info("✅ Voice I/O ready")
            except Exception as e:
                logger.error(f"Voice init failed: {e}")
    
    def init_ui(self):
        """Build modern clean UI."""
        self.setWindowTitle("Jarvis - Modern AI Assistant")
        self.setGeometry(200, 100, 1000, 700)
        self.setMinimumSize(900, 650)
        
        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Use horizontal layout for clean separation
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        
        # Left panel - Orb & Controls
        self.build_left_panel(main_layout)
        
        # Right panel - Conversation
        self.build_right_panel(main_layout)
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {ModernColors.BG_DARK};
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """)
    
    def build_left_panel(self, parent_layout):
        """Build left panel with orb and controls."""
        left_panel = QWidget()
        left_panel.setFixedWidth(450)
        left_panel.setStyleSheet(f"background-color: {ModernColors.BG_DARK};")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        left_panel.setLayout(layout)
        
        # Header
        header = QLabel("JARVIS")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet(f"color: {ModernColors.PRIMARY}; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Status indicator
        self.status_indicator = QLabel("● Ready")
        self.status_indicator.setFont(QFont("Arial", 13))
        self.status_indicator.setStyleSheet(f"color: {ModernColors.SUCCESS};")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_indicator)
        
        # Voice Orb (centered)
        layout.addStretch()
        
        orb_container = QWidget()
        orb_layout = QVBoxLayout()
        orb_layout.setAlignment(Qt.AlignCenter)
        orb_container.setLayout(orb_layout)
        
        self.orb = ModernOrb()
        orb_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        
        layout.addWidget(orb_container)
        layout.addStretch()
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernColors.BG_CARD};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(12)
        input_frame.setLayout(input_layout)
        
        # Text input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command here...")
        self.input_field.setFont(QFont("Arial", 12))
        self.input_field.setMinimumHeight(42)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernColors.BG_DARK};
                color: {ModernColors.TEXT_PRIMARY};
                border: 2px solid {ModernColors.BORDER};
                border-radius: 21px;
                padding: 0 18px;
            }}
            QLineEdit:focus {{
                border-color: {ModernColors.PRIMARY};
            }}
        """)
        self.input_field.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.input_field)
        
        # Buttons row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        
        # Voice button
        self.voice_btn = QPushButton("🎙️ Voice")
        self.voice_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.voice_btn.setMinimumHeight(38)
        self.voice_btn.setCursor(Qt.PointingHandCursor)
        self.voice_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernColors.ACCENT}, stop:1 {ModernColors.ACCENT_LIGHT});
                color: white;
                border: none;
                border-radius: 19px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background: {ModernColors.ACCENT_LIGHT};
            }}
            QPushButton:pressed {{
                background: {ModernColors.ACCENT};
            }}
        """)
        self.voice_btn.clicked.connect(self.toggle_voice)
        button_row.addWidget(self.voice_btn)
        
        # Send button
        send_btn = QPushButton("Send →")
        send_btn.setFont(QFont("Arial", 11, QFont.Bold))
        send_btn.setMinimumHeight(38)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernColors.PRIMARY}, stop:1 {ModernColors.PRIMARY_LIGHT});
                color: white;
                border: none;
                border-radius: 19px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background: {ModernColors.PRIMARY_LIGHT};
            }}
        """)
        send_btn.clicked.connect(self.send_command)
        button_row.addWidget(send_btn)
        
        input_layout.addLayout(button_row)
        layout.addWidget(input_frame)
        
        # Quick commands (simplified)
        quick_label = QLabel("Quick Commands")
        quick_label.setFont(QFont("Arial", 11, QFont.Bold))
        quick_label.setStyleSheet(f"color: {ModernColors.TEXT_SECONDARY}; margin-top: 15px;")
        layout.addWidget(quick_label)
        
        quick_grid = QHBoxLayout()
        quick_grid.setSpacing(8)
        
        quick_cmds = [
            ("⏰", "Time", "what time is it"),
            ("🔋", "Battery", "check battery"),
            ("💻", "System", "show system status"),
        ]
        
        for icon, label_text, cmd in quick_cmds:
            btn = QPushButton(f"{icon}\n{label_text}")
            btn.setFont(QFont("Arial", 9))
            btn.setFixedSize(80, 65)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ModernColors.BG_CARD};
                    color: {ModernColors.TEXT_SECONDARY};
                    border: 1px solid {ModernColors.BORDER};
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    background-color: {ModernColors.BORDER_LIGHT};
                    border-color: {ModernColors.PRIMARY};
                    color: {ModernColors.TEXT_PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.quick_command(c))
            quick_grid.addWidget(btn)
        
        layout.addLayout(quick_grid)
        
        parent_layout.addWidget(left_panel)
    
    def build_right_panel(self, parent_layout):
        """Build right panel with conversation."""
        right_panel = QWidget()
        right_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernColors.BG_CARD};
                border-left: 1px solid {ModernColors.BORDER};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        right_panel.setLayout(layout)
        
        # Conversation title
        title = QLabel("Conversation")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {ModernColors.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        # Conversation area
        self.conversation = QTextBrowser()
        self.conversation.setFont(QFont("Arial", 11))
        self.conversation.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {ModernColors.BG_DARK};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.BORDER};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        self.conversation.setOpenExternalLinks(False)
        self.conversation.setHtml("""
            <div style='color: #9CA3AF; font-size: 11px; margin-bottom: 10px;'>
                Welcome to Jarvis! 👋
            </div>
            <div style='background: #121935; padding: 12px; border-radius: 10px; margin-bottom: 10px;'>
                <b style='color: #3B82F6;'>Jarvis:</b><br>
                <span style='color: #F9FAFB;'>Hello! I'm ready to help. Try saying "what time is it" or "check battery".</span>
            </div>
        """)
        layout.addWidget(self.conversation)
        
        # Footer status
        footer = QLabel("🟢 Voice & Audio Ready")
        footer.setFont(QFont("Arial", 10))
        footer.setStyleSheet(f"color: {ModernColors.TEXT_MUTED};")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        parent_layout.addWidget(right_panel)
    
    def add_message(self, sender, text):
        """Add message to conversation."""
        color = ModernColors.PRIMARY if sender == "jarvis" else ModernColors.ACCENT
        bg = ModernColors.BG_CARD if sender == "jarvis" else "#1E3A5A"
        
        html = f"""
            <div style='background: {bg}; padding: 12px; border-radius: 10px; margin-bottom: 10px;'>
                <b style='color: {color};'>{sender.title()}:</b><br>
                <span style='color: {ModernColors.TEXT_PRIMARY};'>{text}</span>
            </div>
        """
        
        current = self.conversation.toHtml()
        self.conversation.setHtml(current + html)
        
        # Scroll to bottom
        scrollbar = self.conversation.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_status(self, state, text):
        """Update status."""
        colors = {
            "ready": ModernColors.SUCCESS,
            "listening": ModernColors.ACCENT,
            "processing": ModernColors.WARNING,
            "speaking": ModernColors.PRIMARY,
        }
        
        self.status_indicator.setText(f"● {text}")
        self.status_indicator.setStyleSheet(f"color: {colors.get(state, ModernColors.TEXT_SECONDARY)};")
        self.orb.setState(state if state != "ready" else "idle")
    
    def toggle_voice(self):
        """Toggle voice recording - FIXED."""
        if not VOICE_AVAILABLE or not self.stt:
            self.add_message("jarvis", "Voice input not available.")
            return
        
        if self.is_recording:
            # STOP RECORDING MANUALLY
            logger.info("🛑 Stopping recording manually...")
            try:
                sd.stop()
                self.is_recording = False
                self.voice_btn.setText("🎙️ Voice")
                self.set_status("processing", "Processing...")
                
                # The recording thread will process the partial audio
                logger.info("Recording stopped by user")
                
            except Exception as e:
                logger.error(f"Error stopping: {e}")
                self.is_recording = False
                self.voice_btn.setText("🎙️ Voice")
                self.set_status("ready", "Ready")
        else:
            # START RECORDING
            logger.info("🎙️ Starting voice recording...")
            self.is_recording = True
            self.recording_countdown = 5
            self.voice_btn.setText(f"⏹️ Stop (5s)")
            self.set_status("listening", "Listening...")
            
            # Countdown timer
            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self._update_countdown)
            self.countdown_timer.start(1000)  # Every second
            
            def record():
                try:
                    logger.info("Recording 5 seconds of audio...")
                    duration = 5
                    sample_rate = 16000
                    
                    # Record audio
                    audio = sd.rec(
                        int(sample_rate * duration),
                        samplerate=sample_rate,
                        channels=1,
                        dtype='float32'
                    )
                    
                    # Wait for recording to complete
                    sd.wait()
                    
                    logger.info(f"✅ Recording complete ({len(audio)} samples)")
                    
                    # Stop countdown on main thread
                    if hasattr(self, 'countdown_timer'):
                        self.countdown_timer.stop()
                    
                    # Store audio and process on main thread
                    self.recorded_audio = audio[:, 0]  # Get mono channel
                    QTimer.singleShot(0, self._process_recorded_audio)
                        
                except Exception as e:
                    logger.error(f"Recording error: {e}", exc_info=True)
                    if hasattr(self, 'countdown_timer'):
                        QTimer.singleShot(0, lambda: self.countdown_timer.stop())
                    QTimer.singleShot(0, lambda: self._voice_error(str(e)))
            
            import threading
            threading.Thread(target=record, daemon=True).start()
    
    def _update_countdown(self):
        """Update recording countdown."""
        if self.recording_countdown > 0:
            self.recording_countdown -= 1
            self.voice_btn.setText(f"⏹️ Stop ({self.recording_countdown}s)")
        else:
            self.countdown_timer.stop()
    
    def _process_recorded_audio(self):
        """Process stored recorded audio."""
        if not hasattr(self, 'recorded_audio'):
            logger.error("No recorded audio found!")
            self._voice_error("No audio data")
            return
        
        logger.info("Processing recorded audio from storage...")
        self._process_voice(self.recorded_audio)
    
    def _process_voice(self, audio_data):
        """Process voice input - FIXED."""
        logger.info("🎤 Processing voice input...")
        self.is_recording = False
        self.voice_btn.setText("🎙️ Voice")
        self.set_status("processing", "Processing speech...")
        
        try:
            logger.info(f"Transcribing {len(audio_data)} audio samples...")
            
            # Transcribe directly (simpler, more reliable)
            transcript = self.stt.transcribe(audio_data, 16000)
            
            logger.info(f"Raw transcript: '{transcript}'")
            
            if transcript:
                transcript = transcript.strip()
            
            # Check if we got actual speech
            if transcript and len(transcript) > 2:
                logger.info(f"✅ Valid transcript: '{transcript}'")
                self._on_voice_ready(transcript)
            else:
                logger.warning("No speech detected in recording")
                self._no_speech()
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}", exc_info=True)
            self._voice_error(str(e))
    
    def _on_voice_ready(self, transcript):
        """Voice transcript ready - FIXED."""
        logger.info(f"📝 Voice transcript ready: '{transcript}'")
        
        # Show what was heard
        self.input_field.setText(transcript)
        self.add_message("you", f"🎙️ {transcript}")
        
        # Execute the command
        logger.info("Executing voice command...")
        self._execute_command(transcript)
    
    def _no_speech(self):
        """No speech detected - FIXED."""
        logger.info("⚠️ No speech detected")
        self.set_status("speaking", "Speaking...")
        
        msg = "I'm sorry, I didn't hear anything. Please try again."
        self.add_message("jarvis", msg)
        
        # Speak apology
        if self.tts:
            logger.info("Speaking apology...")
            try:
                self.tts.speak(msg)
                logger.info("Apology spoken")
            except Exception as e:
                logger.error(f"TTS apology error: {e}")
            finally:
                self.set_status("ready", "Ready")
        else:
            self.set_status("ready", "Ready")
    
    def _voice_error(self, error):
        """Voice error - FIXED."""
        logger.error(f"❌ Voice error: {error}")
        self.set_status("ready", "Ready")
        
        error_msg = "Sorry, there was an error with voice input."
        self.add_message("jarvis", error_msg)
        
        # Speak error
        if self.tts:
            try:
                self.tts.speak(error_msg)
            except:
                pass
    
    def send_command(self):
        """Send text command."""
        cmd = self.input_field.text().strip()
        if not cmd:
            return
        
        self.input_field.clear()
        self.add_message("you", cmd)
        self._execute_command(cmd)
    
    def quick_command(self, cmd):
        """Quick command."""
        self.input_field.setText(cmd)
        self.send_command()
    
    def _execute_command(self, command):
        """Execute command - COMPLETELY SIMPLIFIED."""
        logger.info(f"📝 Executing command: {command}")
        self.set_status("processing", "Processing...")
        
        # Delay slightly to show processing state
        QTimer.singleShot(100, lambda: self._do_execute(command))
    
    def _do_execute(self, command):
        """Actually execute the command."""
        try:
            import asyncio
            
            logger.info("1. Classifying...")
            intent = self.classifier.classify(command)
            logger.info(f"2. Intent: {intent.type} (confidence: {intent.confidence:.2f})")
            
            logger.info("3. Routing to handler...")
            result = asyncio.run(self.router.route(intent))
            logger.info(f"4. Got result: {result.message[:100] if result.message else 'None'}")
            
            # Show response immediately
            if result and result.message:
                logger.info("5. Showing response...")
                self._show_response(result.message)
            else:
                logger.warning("No response!")
                self._show_response("I processed that but have no response.")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            self._show_response(f"Error: {str(e)}")
    
    def _show_response(self, text):
        """Show and speak response - FIXED."""
        logger.info(f"✅ _show_response called with: {text[:100]}")
        
        try:
            # Update UI immediately
            self.set_status("speaking", "Speaking...")
            self.add_message("jarvis", text)
            logger.info("Message added to conversation")
            
            # Force UI update
            QApplication.processEvents()
            
            # Speak if available
            if self.tts and text:
                logger.info("🔊 Starting TTS...")
                
                def speak():
                    try:
                        logger.info(f"TTS speaking: {text[:50]}...")
                        success = self.tts.speak(text)
                        
                        if success:
                            logger.info("✅ TTS playback complete")
                        else:
                            logger.warning("⚠️ TTS returned False")
                            
                    except Exception as e:
                        logger.error(f"❌ TTS error: {e}", exc_info=True)
                    finally:
                        # Return to ready
                        logger.info("Returning to ready...")
                        QTimer.singleShot(0, self._return_to_ready)
                
                import threading
                threading.Thread(target=speak, daemon=True).start()
            else:
                # No TTS
                logger.warning("TTS not available or no text")
                self._return_to_ready()
                
        except Exception as e:
            logger.error(f"❌ _show_response error: {e}", exc_info=True)
            self._return_to_ready()
    
    def _return_to_ready(self):
        """Return to ready state."""
        logger.info("🔄 Returning to ready state")
        self.set_status("ready", "Ready")
        logger.info("✅ Status set to Ready")
    
    def closeEvent(self, event):
        """Cleanup."""
        if hasattr(self, 'reminder_skills'):
            self.reminder_skills.shutdown()
        event.accept()


def main():
    """Launch Modern Jarvis."""
    logger.info("🚀 Starting Modern Jarvis UI...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis Modern")
    
    window = JarvisModernUI()
    window.show()
    
    logger.info("✨ Modern UI launched!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

