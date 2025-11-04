"""
Jarvis Desktop UI - Main Window
Simple, clean interface for Jarvis assistant.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QStatusBar
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.router import CommandRouter
from core.skills.information import InformationSkills
from core.skills.system import SystemSkills
from core.skills.reminders import ReminderSkills
import asyncio


class CommandWorker(QThread):
    """Worker thread for processing commands."""
    
    result_ready = Signal(str)
    
    def __init__(self, classifier, router, command):
        super().__init__()
        self.classifier = classifier
        self.router = router
        self.command = command
    
    def run(self):
        """Process command in background."""
        try:
            intent = self.classifier.classify(self.command)
            result = asyncio.run(self.router.route(intent))
            self.result_ready.emit(result.message)
        except Exception as e:
            self.result_ready.emit(f"Error: {str(e)}")


class JarvisMainWindow(QMainWindow):
    """Main window for Jarvis desktop UI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_jarvis()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Jarvis - Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("🤖 JARVIS")
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        # Conversation history
        history_label = QLabel("Conversation History:")
        layout.addWidget(history_label)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.history_text)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command here (e.g., 'what time is it')")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)
        self.input_field.returnPressed.connect(self.process_command)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.send_button.clicked.connect(self.process_command)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Quick action buttons
        button_layout = QHBoxLayout()
        
        quick_commands = [
            ("🕒 Time", "what time is it"),
            ("📅 Date", "what's the date"),
            ("🔋 Battery", "check battery"),
            ("💻 System", "system info"),
            ("❓ Help", "help"),
        ]
        
        for label, command in quick_commands:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
            """)
            btn.clicked.connect(lambda checked, cmd=command: self.quick_command(cmd))
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def init_jarvis(self):
        """Initialize Jarvis components."""
        import logging
        logging.getLogger().setLevel(logging.ERROR)
        
        self.classifier = IntentClassifier()
        self.router = CommandRouter()
        self.info_skills = InformationSkills()
        self.system_skills = SystemSkills()
        self.reminder_skills = ReminderSkills()
        
        # Register handlers
        info_intents = [
            IntentType.GET_TIME, IntentType.GET_DATE, IntentType.GET_SYSTEM_INFO,
            IntentType.GET_BATTERY, IntentType.HELP, IntentType.THANK_YOU
        ]
        for intent_type in info_intents:
            self.router.register_handler(intent_type, self.info_skills.handle_intent)
        
        system_intents = [
            IntentType.VOLUME_UP, IntentType.VOLUME_DOWN, IntentType.VOLUME_SET,
            IntentType.MUTE, IntentType.UNMUTE
        ]
        for intent_type in system_intents:
            self.router.register_handler(intent_type, self.system_skills.handle_intent)
        
        reminder_intents = [
            IntentType.SET_TIMER, IntentType.LIST_REMINDERS
        ]
        for intent_type in reminder_intents:
            self.router.register_handler(intent_type, self.reminder_skills.handle_intent)
        
        self.add_to_history("[System] Jarvis initialized successfully!")
        self.add_to_history("[System] Ready to receive commands\n")
    
    def add_to_history(self, message: str):
        """Add message to conversation history."""
        self.history_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.history_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @Slot()
    def quick_command(self, command: str):
        """Execute a quick command button."""
        self.input_field.setText(command)
        self.process_command()
    
    @Slot()
    def process_command(self):
        """Process user command."""
        command = self.input_field.text().strip()
        
        if not command:
            return
        
        # Clear input
        self.input_field.clear()
        
        # Add to history
        self.add_to_history(f"\n👤 You: {command}")
        
        # Update status
        self.status_label.setText("Status: Processing...")
        self.status_label.setStyleSheet("color: orange; font-size: 14px;")
        self.status_bar.showMessage("Processing command...")
        
        # Process in background thread
        self.worker = CommandWorker(self.classifier, self.router, command)
        self.worker.result_ready.connect(self.on_result_ready)
        self.worker.start()
    
    @Slot(str)
    def on_result_ready(self, result: str):
        """Handle command result."""
        self.add_to_history(f"🤖 Jarvis: {result}")
        
        # Update status
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("color: green; font-size: 14px;")
        self.status_bar.showMessage("Ready")
        
        # Focus back to input
        self.input_field.setFocus()
    
    def closeEvent(self, event):
        """Handle window close."""
        self.reminder_skills.shutdown()
        event.accept()




