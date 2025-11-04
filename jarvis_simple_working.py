"""
Jarvis Simple Working UI
Absolutely reliable - no complex threading
"""

import sys
import io

# Fix Windows console encoding FIRST
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import asyncio
import logging

sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
from core.nlu.router import CommandRouter

# Voice
try:
    import sounddevice as sd
    import numpy as np
    from core.audio.stt_faster_whisper import create_faster_whisper
    from simple_tts import SimpleTTS
    VOICE_OK = True
except:
    VOICE_OK = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleJarvisUI(QMainWindow):
    """Super simple Jarvis UI that absolutely works."""
    
    def __init__(self):
        super().__init__()
        
        print("="*60)
        print("INITIALIZING SIMPLE JARVIS...")
        print("="*60)
        
        # Backend
        print("Loading NLU...")
        self.classifier = IntentClassifier()
        self.router = CommandRouter()
        
        print("Loading skills...")
        self.info = InformationSkills()
        self.system = SystemSkills()
        self.reminders = ReminderSkills()
        
        # Register
        for i in [IntentType.GET_TIME, IntentType.GET_DATE, IntentType.GET_BATTERY, 
                  IntentType.GET_SYSTEM_INFO, IntentType.HELP]:
            self.router.register_handler(i, self.info.handle_intent)
        
        for i in [IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, IntentType.VOLUME_SET]:
            self.router.register_handler(i, self.system.handle_intent)
        
        for i in [IntentType.SET_TIMER, IntentType.LIST_REMINDERS]:
            self.router.register_handler(i, self.reminders.handle_intent)
        
        # Voice
        self.stt = None
        self.tts = None
        self.recording = False
        
        if VOICE_OK:
            print("Loading voice engines...")
            self.stt = create_faster_whisper(model_size="tiny")
            self.tts = SimpleTTS()
            print("[OK] Voice ready!")
        
        print("Building UI...")
        self.setup_ui()
        print("[OK] JARVIS READY!")
        print("="*60)
    
    def setup_ui(self):
        """Setup UI."""
        self.setWindowTitle("Jarvis - Simple & Working")
        self.setGeometry(200, 100, 900, 600)
        
        # Main
        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        main.setLayout(layout)
        
        # LEFT PANEL
        left = QWidget()
        left.setFixedWidth(400)
        left.setStyleSheet("background: #0A0E27;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        left.setLayout(left_layout)
        
        # Title
        title = QLabel("JARVIS")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #3B82F6;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # Status
        self.status = QLabel("● Ready")
        self.status.setFont(QFont("Arial", 12))
        self.status.setStyleSheet("color: #10B981;")
        self.status.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status)
        
        left_layout.addStretch()
        
        # Input
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type command...")
        self.input.setFont(QFont("Arial", 11))
        self.input.setMinimumHeight(40)
        self.input.setStyleSheet("""
            QLineEdit {
                background: #121935;
                color: white;
                border: 2px solid #1F2937;
                border-radius: 20px;
                padding: 0 15px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
        """)
        self.input.returnPressed.connect(self.send_text)
        left_layout.addWidget(self.input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.voice_btn = QPushButton("🎙️ Voice")
        self.voice_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.voice_btn.setMinimumHeight(36)
        self.voice_btn.setCursor(Qt.PointingHandCursor)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: #06B6D4;
                color: white;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover { background: #22D3EE; }
        """)
        self.voice_btn.clicked.connect(self.voice_click)
        btn_layout.addWidget(self.voice_btn)
        
        send = QPushButton("Send")
        send.setFont(QFont("Arial", 10, QFont.Bold))
        send.setMinimumHeight(36)
        send.setCursor(Qt.PointingHandCursor)
        send.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover { background: #60A5FA; }
        """)
        send.clicked.connect(self.send_text)
        btn_layout.addWidget(send)
        
        left_layout.addLayout(btn_layout)
        
        # Quick buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        
        for icon, cmd in [("⏰", "what time is it"), ("🔋", "check battery"), ("💻", "system info")]:
            btn = QPushButton(icon)
            btn.setFont(QFont("Arial", 16))
            btn.setFixedSize(70, 55)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: #121935;
                    color: #9CA3AF;
                    border: 1px solid #1F2937;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background: #1F2937;
                    color: white;
                    border-color: #3B82F6;
                }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.quick_cmd(c))
            quick_layout.addWidget(btn)
        
        left_layout.addLayout(quick_layout)
        
        layout.addWidget(left)
        
        # RIGHT PANEL
        right = QWidget()
        right.setStyleSheet("background: #121935; border-left: 1px solid #1F2937;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(10)
        right.setLayout(right_layout)
        
        conv_title = QLabel("Conversation")
        conv_title.setFont(QFont("Arial", 14, QFont.Bold))
        conv_title.setStyleSheet("color: white;")
        right_layout.addWidget(conv_title)
        
        self.conversation = QTextBrowser()
        self.conversation.setFont(QFont("Arial", 10))
        self.conversation.setStyleSheet("""
            QTextBrowser {
                background: #0A0E27;
                color: white;
                border: 1px solid #1F2937;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.conversation.setHtml("<p style='color: #6B7280;'>Welcome! Type or speak a command.</p>")
        right_layout.addWidget(self.conversation)
        
        footer = QLabel("🟢 Ready")
        footer.setFont(QFont("Arial", 9))
        footer.setStyleSheet("color: #6B7280;")
        right_layout.addWidget(footer)
        
        layout.addWidget(right)
        
        # Dark theme
        self.setStyleSheet("QMainWindow { background: #0A0E27; }")
    
    def add_msg(self, sender, text):
        """Add message."""
        color = "#3B82F6" if sender == "Jarvis" else "#06B6D4"
        html = f"<p style='margin: 5px 0;'><b style='color: {color};'>{sender}:</b> <span style='color: white;'>{text}</span></p>"
        current = self.conversation.toHtml()
        self.conversation.setHtml(current + html)
        self.conversation.verticalScrollBar().setValue(
            self.conversation.verticalScrollBar().maximum()
        )
    
    def voice_click(self):
        """Voice button clicked."""
        if not VOICE_OK or not self.stt:
            self.add_msg("Jarvis", "Voice not available")
            return
        
        if self.recording:
            # STOP
            print("🛑 Stopping recording...")
            sd.stop()
            self.recording = False
            self.voice_btn.setText("🎙️ Voice")
            self.status.setText("● Ready")
            self.status.setStyleSheet("color: #10B981;")
        else:
            # START
            print("🎙️ Starting recording...")
            self.recording = True
            self.voice_btn.setText("⏹️ Stop")
            self.status.setText("● Recording...")
            self.status.setStyleSheet("color: #06B6D4;")
            
            # Start recording in background
            self.start_recording()
    
    def start_recording(self):
        """Start 5-second recording."""
        print("Recording 5 seconds...")
        
        # Create timer that processes after 5 seconds
        QTimer.singleShot(5000, self.process_recording)
        
        # Start actual recording
        self.audio_data = sd.rec(
            int(16000 * 5),
            samplerate=16000,
            channels=1,
            dtype='float32'
        )
    
    def process_recording(self):
        """Process recorded audio."""
        if not self.recording:
            return
        
        print("⏹️ Recording finished, processing...")
        self.recording = False
        self.voice_btn.setText("🎙️ Voice")
        self.status.setText("● Processing...")
        self.status.setStyleSheet("color: #F59E0B;")
        
        # Wait for recording to finish
        sd.wait()
        
        # Get audio
        audio = self.audio_data[:, 0]
        print(f"Got {len(audio)} samples")
        
        # Transcribe
        print("Transcribing...")
        try:
            transcript = self.stt.transcribe(audio, 16000)
            print(f"Transcript: '{transcript}'")
            
            if transcript and len(transcript.strip()) > 2:
                transcript = transcript.strip()
                self.add_msg("You", f"🎙️ {transcript}")
                self.process_cmd(transcript)
            else:
                print("No speech detected")
                self.add_msg("Jarvis", "I didn't hear anything.")
                if self.tts:
                    self.tts.speak("I didn't hear anything. Please try again.")
                self.status.setText("● Ready")
                self.status.setStyleSheet("color: #10B981;")
        except Exception as e:
            print(f"Error: {e}")
            self.add_msg("Jarvis", f"Error: {e}")
            self.status.setText("● Ready")
            self.status.setStyleSheet("color: #10B981;")
    
    def send_text(self):
        """Send text command."""
        cmd = self.input.text().strip()
        if not cmd:
            return
        
        print(f"Text command: {cmd}")
        self.input.clear()
        self.add_msg("You", cmd)
        self.process_cmd(cmd)
    
    def quick_cmd(self, cmd):
        """Quick command."""
        print(f"Quick: {cmd}")
        self.input.setText(cmd)
        self.send_text()
    
    def process_cmd(self, command):
        """Process command - SIMPLE."""
        print(f"Processing: {command}")
        self.status.setText("● Processing...")
        self.status.setStyleSheet("color: #F59E0B;")
        
        # Force UI update
        QApplication.processEvents()
        
        try:
            # Classify
            print("  1. Classifying...")
            intent = self.classifier.classify(command)
            print(f"  2. Intent: {intent.type}")
            
            # Route
            print("  3. Routing...")
            result = asyncio.run(self.router.route(intent))
            print(f"  4. Result: {result.message}")
            
            # Show
            if result and result.message:
                self.status.setText("● Speaking...")
                self.status.setStyleSheet("color: #3B82F6;")
                self.add_msg("Jarvis", result.message)
                
                # Force UI update
                QApplication.processEvents()
                
                # Speak
                if self.tts:
                    print("  5. Speaking...")
                    self.tts.speak(result.message)
                    print("  6. Done!")
                
                self.status.setText("● Ready")
                self.status.setStyleSheet("color: #10B981;")
            else:
                print("  ERROR: No result!")
                self.add_msg("Jarvis", "No response")
                self.status.setText("● Ready")
                self.status.setStyleSheet("color: #10B981;")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.add_msg("Jarvis", f"Error: {e}")
            self.status.setText("● Ready")
            self.status.setStyleSheet("color: #10B981;")
    
    def closeEvent(self, event):
        """Cleanup."""
        if hasattr(self, 'reminders'):
            self.reminders.shutdown()
        event.accept()


def main():
    print("\n" + "="*60)
    print("STARTING SIMPLE JARVIS UI")
    print("="*60 + "\n")
    
    app = QApplication(sys.argv)
    window = SimpleJarvisUI()
    window.show()
    
    print("\n[OK] UI IS RUNNING!")
    print("Try: Type 'what time is it' and press Enter")
    print("="*60 + "\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

