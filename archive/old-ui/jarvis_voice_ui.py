"""
Jarvis Voice-Enabled UI
Secure voice assistant with local processing
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QStatusBar, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.audio.secure_microphone import SecureMicrophone, AudioConfig, AudioLevelMonitor
from core.audio.secure_stt import create_stt
from core.audio.secure_tts import create_tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecordingThread(QThread):
    """Thread for voice recording."""
    
    finished = Signal(bytes)  # Audio data
    error = Signal(str)
    level_update = Signal(float)  # Audio level 0-1
    
    def __init__(self, microphone: SecureMicrophone):
        super().__init__()
        self.microphone = microphone
        self.level_monitor = AudioLevelMonitor(microphone)
    
    def run(self):
        """Run recording."""
        try:
            # Start recording with level monitoring
            success = self.microphone.start_recording(
                callback=lambda chunk: self.level_update.emit(
                    self.microphone.get_audio_level(chunk)
                )
            )
            
            if not success:
                self.error.emit("Failed to start recording")
                return
            
            # Recording happens in background...
            # When stopped externally, emit finished signal
            
        except Exception as e:
            logger.error(f"Recording thread error: {e}", exc_info=True)
            self.error.emit(str(e))


class VoiceProcessingThread(QThread):
    """Thread for voice processing (STT + Intent + TTS)."""
    
    finished = Signal(str)  # Result message
    error = Signal(str)
    progress = Signal(str)  # Progress message
    
    def __init__(self, audio_data: bytes, stt, classifier, skills, tts):
        super().__init__()
        self.audio_data = audio_data
        self.stt = stt
        self.classifier = classifier
        self.skills = skills
        self.tts = tts
    
    def run(self):
        """Process voice command."""
        try:
            # Step 1: Transcribe
            self.progress.emit("🎤 Transcribing audio...")
            stt_result = self.stt.transcribe_bytes(self.audio_data, sample_rate=16000)
            
            if not stt_result.success or not stt_result.text:
                self.error.emit("Could not understand audio")
                return
            
            command = stt_result.text
            self.progress.emit(f"📝 Heard: {command}")
            logger.info(f"Transcribed: {command}")
            
            # Step 2: Classify intent
            self.progress.emit("🧠 Understanding command...")
            intent = self.classifier.classify(command)
            
            # Step 3: Execute
            self.progress.emit("⚙️ Executing...")
            
            if intent.type.value in ["get_time", "get_date"]:
                result = self.skills['info'].handle_intent(intent)
            elif intent.type.value.startswith("volume"):
                result = self.skills['system'].handle_intent(intent)
            else:
                result = self.skills['info'].handle_intent(intent)
            
            response_text = result.message
            
            # Step 4: Speak response
            if result.success and response_text:
                self.progress.emit("🔊 Speaking response...")
                logger.info(f"Speaking: {response_text}")
                self.tts.speak(response_text)
            
            # Done
            full_response = f"Command: {command}\n"
            full_response += f"Intent: {intent.type.value}\n"
            full_response += f"Response: {response_text}"
            
            self.finished.emit(full_response)
            
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            self.error.emit(str(e))


class JarvisVoiceUI(QMainWindow):
    """Voice-enabled Jarvis UI."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize backend
        logger.info("Initializing Jarvis Voice Backend...")
        self.classifier = IntentClassifier()
        self.info_skills = InformationSkills()
        self.system_skills = SystemSkills()
        self.skills = {
            'info': self.info_skills,
            'system': self.system_skills
        }
        
        # Initialize audio
        self.microphone = SecureMicrophone(AudioConfig())
        self.stt = create_stt(model_size="base")
        self.tts = create_tts(voice="en-US-AriaNeural")
        
        # State
        self.is_recording = False
        self.recording_thread = None
        self.processing_thread = None
        
        logger.info("Backend initialized")
        
        self.init_ui()
        
        # Check STT/TTS availability
        QTimer.singleShot(500, self.check_audio_availability)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🎤 Jarvis Voice Assistant")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎤 JARVIS VOICE")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #4A90E2; margin: 15px;")
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Ready to listen")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Arial", 14)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Audio level indicator
        self.level_bar = QProgressBar()
        self.level_bar.setMaximum(100)
        self.level_bar.setValue(0)
        self.level_bar.setTextVisible(False)
        self.level_bar.setMaximumHeight(20)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498DB;
                border-radius: 5px;
                background-color: #34495E;
            }
            QProgressBar::chunk {
                background-color: #2ECC71;
            }
        """)
        layout.addWidget(self.level_bar)
        
        # Voice button (large, prominent)
        self.voice_btn = QPushButton("🎤 HOLD TO TALK")
        self.voice_btn.setMinimumHeight(120)
        self.voice_btn.setFont(QFont("Arial", 18, QFont.Bold))
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 60px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #E74C3C;
            }
        """)
        # Press and hold behavior
        self.voice_btn.pressed.connect(self.start_voice_recording)
        self.voice_btn.released.connect(self.stop_voice_recording)
        layout.addWidget(self.voice_btn)
        
        # Instructions
        instructions = QLabel("💡 Hold the button and speak your command\nRelease to process")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 10))
        instructions.setStyleSheet("color: #95A5A6; margin: 5px;")
        layout.addWidget(instructions)
        
        # Quick text commands
        text_layout = QVBoxLayout()
        text_label = QLabel("⌨️ Or type a command:")
        text_label.setFont(QFont("Arial", 11))
        text_layout.addWidget(text_label)
        
        text_input_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type command here...")
        self.text_input.setMaximumHeight(60)
        self.text_input.setFont(QFont("Arial", 11))
        text_input_layout.addWidget(self.text_input)
        
        self.text_btn = QPushButton("Send")
        self.text_btn.setMinimumWidth(100)
        self.text_btn.setMinimumHeight(60)
        self.text_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.text_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.text_btn.clicked.connect(self.process_text_command)
        text_input_layout.addWidget(self.text_btn)
        
        text_layout.addLayout(text_input_layout)
        layout.addLayout(text_layout)
        
        # Response area
        response_label = QLabel("📋 Transcript & Response:")
        response_label.setFont(QFont("Arial", 11))
        layout.addWidget(response_label)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setFont(QFont("Courier New", 10))
        self.response_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.response_text)
        
        central_widget.setLayout(layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("🎙️ Voice assistant ready!")
        
        # Apply theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel {
                color: #ECF0F1;
            }
        """)
    
    def check_audio_availability(self):
        """Check if audio components are available."""
        messages = []
        
        if not self.stt.is_available():
            messages.append("⚠️ STT not available - install faster-whisper")
        
        if not self.tts.is_available():
            messages.append("⚠️ TTS not available - install edge-tts and pygame")
        
        if messages:
            self.response_text.append("\n".join(messages))
            self.response_text.append("\nInstall with:")
            self.response_text.append("  pip install faster-whisper edge-tts pygame")
    
    def start_voice_recording(self):
        """Start recording voice."""
        if self.is_recording:
            return
        
        logger.info("Starting voice recording...")
        self.is_recording = True
        
        # Update UI
        self.voice_btn.setText("🔴 RECORDING... (Release to process)")
        self.status_label.setText("🎤 Listening...")
        self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
        self.response_text.append("\n--- Recording started ---")
        
        # Start recording
        self.microphone.start_recording(
            callback=lambda chunk: self.update_audio_level(chunk)
        )
    
    def stop_voice_recording(self):
        """Stop recording and process."""
        if not self.is_recording:
            return
        
        logger.info("Stopping voice recording...")
        self.is_recording = False
        
        # Update UI
        self.voice_btn.setText("⏳ Processing...")
        self.voice_btn.setEnabled(False)
        self.status_label.setText("⏳ Processing audio...")
        self.status_label.setStyleSheet("color: #F39C12; margin: 10px;")
        self.level_bar.setValue(0)
        
        # Stop recording and get data
        audio_data = self.microphone.stop_recording()
        
        if len(audio_data) < 1000:  # Too short
            self.response_text.append("❌ Recording too short - please speak longer")
            self.reset_ui()
            return
        
        # Process in background thread
        self.processing_thread = VoiceProcessingThread(
            audio_data, self.stt, self.classifier, self.skills, self.tts
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_complete)
        self.processing_thread.error.connect(self.processing_error)
        self.processing_thread.start()
    
    def update_audio_level(self, chunk: bytes):
        """Update audio level indicator."""
        level = self.microphone.get_audio_level(chunk)
        self.level_bar.setValue(int(level * 100))
    
    def update_progress(self, message: str):
        """Update progress message."""
        self.status_label.setText(message)
        self.response_text.append(message)
    
    def processing_complete(self, result: str):
        """Processing complete."""
        self.response_text.append("\n" + "="*50)
        self.response_text.append(result)
        self.response_text.append("="*50 + "\n")
        self.reset_ui()
    
    def processing_error(self, error: str):
        """Processing error."""
        self.response_text.append(f"\n❌ Error: {error}\n")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI to ready state."""
        self.voice_btn.setText("🎤 HOLD TO TALK")
        self.voice_btn.setEnabled(True)
        self.status_label.setText("Ready to listen")
        self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;")
        self.level_bar.setValue(0)
    
    def process_text_command(self):
        """Process typed text command."""
        command = self.text_input.toPlainText().strip()
        
        if not command:
            return
        
        self.text_input.clear()
        self.response_text.append(f"\n📝 Text Command: {command}")
        
        try:
            # Classify and execute
            intent = self.classifier.classify(command)
            
            if intent.type.value in ["get_time", "get_date"]:
                result = self.info_skills.handle_intent(intent)
            elif intent.type.value.startswith("volume"):
                result = self.system_skills.handle_intent(intent)
            else:
                result = self.info_skills.handle_intent(intent)
            
            # Display result
            self.response_text.append(f"Intent: {intent.type.value}")
            self.response_text.append(f"Response: {result.message}")
            
            # Speak response
            if result.success and result.message:
                self.tts.speak(result.message)
            
        except Exception as e:
            self.response_text.append(f"❌ Error: {e}")
            logger.error(f"Text command error: {e}", exc_info=True)
    
    def closeEvent(self, event):
        """Clean up on close."""
        logger.info("Shutting down...")
        
        if self.is_recording:
            self.microphone.stop_recording()
        
        self.microphone.cleanup()
        self.tts.stop()
        
        event.accept()


def main():
    """Main entry point."""
    logger.info("Starting Jarvis Voice UI...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis Voice")
    
    window = JarvisVoiceUI()
    window.show()
    
    logger.info("Voice UI started successfully!")
    logger.info("Hold the button and speak your command!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

