"""
Simple Working Jarvis UI with Voice Support
Alternative approach using basic Qt Widgets + Voice I/O
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.nlu.intents import IntentClassifier
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.audio.voice_manager import VoiceManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JarvisSimpleUI(QMainWindow):
    """Simple Jarvis UI with Qt Widgets and Voice Support."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize backend
        logger.info("Initializing Jarvis backend...")
        self.classifier = IntentClassifier()
        self.info_skills = InformationSkills()
        self.system_skills = SystemSkills()
        
        # Initialize voice manager
        logger.info("Initializing Voice Manager...")
        self.voice_manager = VoiceManager(
            stt_model="base",
            tts_voice="en-US-AriaNeural"
        )
        self.is_listening = False
        
        logger.info("Backend initialized")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Jarvis - Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🤖 JARVIS")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 32, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #4A90E2; margin: 20px;")
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Arial", 16)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Input area
        input_label = QLabel("Type your command:")
        input_label.setFont(QFont("Arial", 12))
        layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("e.g., 'what time is it', 'set volume to 50', 'show system status'")
        self.input_text.setMaximumHeight(80)
        self.input_text.setFont(QFont("Arial", 12))
        layout.addWidget(self.input_text)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        # Voice buttons row
        voice_layout = QHBoxLayout()
        
        # Listen button
        self.listen_btn = QPushButton("🎤 Start Listening")
        self.listen_btn.setMinimumHeight(50)
        self.listen_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.listen_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
            }
        """)
        self.listen_btn.clicked.connect(self.toggle_listening)
        self.listen_btn.setEnabled(self.voice_manager.voice_input_available and self.voice_manager.stt_available)
        voice_layout.addWidget(self.listen_btn)
        
        # Process text button
        self.process_btn = QPushButton("⌨️ Process Text")
        self.process_btn.setMinimumHeight(50)
        self.process_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2E5F8E;
            }
        """)
        self.process_btn.clicked.connect(self.process_command)
        voice_layout.addWidget(self.process_btn)
        
        button_layout.addLayout(voice_layout)
        
        # Quick action buttons
        quick_layout = QVBoxLayout()
        quick_label = QLabel("Quick Actions:")
        quick_label.setFont(QFont("Arial", 10))
        quick_layout.addWidget(quick_label)
        
        quick_buttons = [
            ("⏰ What time is it?", "what time is it"),
            ("📅 What's the date?", "what's the date"),
            ("💾 Show system status", "show system status"),
            ("🔊 Get volume", "get volume"),
        ]
        
        for label, command in quick_buttons:
            btn = QPushButton(label)
            btn.setFont(QFont("Arial", 10))
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ECF0F1;
                    border: 1px solid #BDC3C7;
                    border-radius: 3px;
                    text-align: left;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #D5DBDB;
                }
            """)
            btn.clicked.connect(lambda checked, c=command: self.quick_command(c))
            quick_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        layout.addLayout(quick_layout)
        
        # Response area
        response_label = QLabel("Response:")
        response_label.setFont(QFont("Arial", 12))
        layout.addWidget(response_label)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setFont(QFont("Courier New", 11))
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
        self.statusBar.showMessage("Jarvis initialized and ready!")
        
        # Apply dark theme
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
    
    def quick_command(self, command):
        """Execute a quick command."""
        self.input_text.setText(command)
        self.process_command()
    
    def toggle_listening(self):
        """Toggle voice listening on/off."""
        if not self.is_listening:
            # Start listening
            if self.voice_manager.start_listening():
                self.is_listening = True
                self.listen_btn.setText("🔴 Stop Listening")
                self.listen_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E67E22;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #D35400;
                    }
                """)
                self.status_label.setText("🎤 Listening...")
                self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
                self.process_btn.setEnabled(False)
            else:
                self.response_text.setText("Error: Could not start voice input")
        else:
            # Stop listening and transcribe
            self.status_label.setText("Processing speech...")
            self.status_label.setStyleSheet("color: #F39C12; margin: 10px;")
            
            # Stop listening in background
            QTimer.singleShot(100, self._process_voice_input)
    
    def _process_voice_input(self):
        """Process voice input after stopping recording."""
        try:
            transcribed_text = self.voice_manager.stop_listening()
            
            self.is_listening = False
            self.listen_btn.setText("🎤 Start Listening")
            self.listen_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
            self.process_btn.setEnabled(True)
            
            if transcribed_text:
                logger.info(f"Voice input: {transcribed_text}")
                self.input_text.setText(transcribed_text)
                self.status_label.setText("✓ Transcribed!")
                self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;")
                
                # Auto-process the voice command
                QTimer.singleShot(500, self.process_command)
            else:
                self.status_label.setText("⚠ No speech detected")
                self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
                self.response_text.setText("No speech detected. Please try again.")
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}", exc_info=True)
            self.status_label.setText("✗ Error")
            self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
            self.response_text.setText(f"Voice processing error: {str(e)}")
            self.is_listening = False
            self.process_btn.setEnabled(True)
    
    def process_command(self):
        """Process the user's command."""
        command = self.input_text.toPlainText().strip()
        
        if not command:
            self.response_text.setText("Please enter a command.")
            return
        
        self.status_label.setText("Processing...")
        self.status_label.setStyleSheet("color: #F39C12; margin: 10px;")
        
        try:
            # Classify intent
            intent = self.classifier.classify(command)
            
            # Route to appropriate skill
            if intent.type.value in ["get_time", "get_date"]:
                result = self.info_skills.handle_intent(intent)
            elif intent.type.value.startswith("volume"):
                result = self.system_skills.handle_intent(intent)
            elif intent.type.value == "get_system_info":
                from core.skills.system_snapshot import SystemSnapshotSkills
                snapshot_skills = SystemSnapshotSkills()
                result = snapshot_skills.get_snapshot_summary()
            else:
                result = self.info_skills.handle_intent(intent)
            
            # Display result
            response_text = f"Command: {command}\n"
            response_text += f"Intent: {intent.type.value} (confidence: {intent.confidence:.2f})\n"
            response_text += f"\nResponse:\n{result.message}\n"
            
            if result.success:
                self.status_label.setText("✓ Success!")
                self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;")
            else:
                self.status_label.setText("⚠ Warning")
                self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
            
            self.response_text.setText(response_text)
            self.statusBar.showMessage(f"Processed: {intent.type.value}")
            
            # Speak the response if TTS is available
            if self.voice_manager.tts_available and result.message:
                logger.info("Speaking response...")
                self.voice_manager.speak(result.message)
            
            # Reset status after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
            QTimer.singleShot(3000, lambda: self.status_label.setStyleSheet("color: #2ECC71; margin: 10px;"))
            
        except Exception as e:
            error_text = f"Error: {str(e)}"
            self.response_text.setText(error_text)
            self.status_label.setText("✗ Error")
            self.status_label.setStyleSheet("color: #E74C3C; margin: 10px;")
            logger.error(f"Error processing command: {e}", exc_info=True)


def main():
    """Main entry point."""
    logger.info("Starting Jarvis Simple UI...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis")
    
    window = JarvisSimpleUI()
    window.show()
    
    logger.info("UI started successfully!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


