"""
First-Run Wizard for Jarvis

Interactive setup wizard for initial configuration:
1. Welcome screen
2. Audio device selection
3. Wake word calibration
4. STT/TTS selection
5. Privacy settings
6. Account linking (optional)
7. Quick tour
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QLineEdit, QTextEdit,
    QGroupBox, QRadioButton, QProgressBar, QSlider, QListWidget
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap
from loguru import logger
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config.config_manager import ConfigManager


@dataclass
class SetupConfig:
    """Configuration collected from wizard."""
    audio_input_device: Optional[str] = None
    audio_output_device: Optional[str] = None
    wake_word_enabled: bool = True
    wake_word_sensitivity: float = 0.5
    stt_backend: str = "offline"  # "offline" or "cloud"
    tts_backend: str = "offline"  # "offline" or "cloud"
    openai_api_key: Optional[str] = None
    telemetry_enabled: bool = False
    crash_reports_enabled: bool = True
    autostart_enabled: bool = True
    google_calendar_enabled: bool = False


class WelcomePage(QWizardPage):
    """Welcome page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Jarvis")
        self.setSubTitle("Your AI-powered voice assistant")
        
        layout = QVBoxLayout()
        
        # Logo (placeholder)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setText("🤖")
        logo_label.setStyleSheet("font-size: 72px;")
        layout.addWidget(logo_label)
        
        # Welcome message
        message = QLabel(
            "Welcome to Jarvis!\n\n"
            "This wizard will help you set up your voice assistant.\n\n"
            "We'll configure:\n"
            "• Audio devices\n"
            "• Wake word detection\n"
            "• Speech recognition\n"
            "• Privacy settings\n\n"
            "This should take about 5 minutes."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch()
        self.setLayout(layout)


class AudioDevicePage(QWizardPage):
    """Audio device selection page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Audio Devices")
        self.setSubTitle("Select your microphone and speakers")
        
        layout = QVBoxLayout()
        
        # Input device
        input_group = QGroupBox("Microphone")
        input_layout = QVBoxLayout()
        
        self.input_combo = QComboBox()
        self.input_combo.addItem("Default Microphone", None)
        input_layout.addWidget(QLabel("Select your microphone:"))
        input_layout.addWidget(self.input_combo)
        
        test_mic_btn = QPushButton("Test Microphone")
        test_mic_btn.clicked.connect(self._test_microphone)
        input_layout.addWidget(test_mic_btn)
        
        self.mic_level = QProgressBar()
        self.mic_level.setRange(0, 100)
        input_layout.addWidget(self.mic_level)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output device
        output_group = QGroupBox("Speakers")
        output_layout = QVBoxLayout()
        
        self.output_combo = QComboBox()
        self.output_combo.addItem("Default Speakers", None)
        output_layout.addWidget(QLabel("Select your speakers:"))
        output_layout.addWidget(self.output_combo)
        
        test_speaker_btn = QPushButton("Test Speakers")
        test_speaker_btn.clicked.connect(self._test_speakers)
        output_layout.addWidget(test_speaker_btn)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Load devices
        self._load_audio_devices()
    
    def _load_audio_devices(self):
        """Load available audio devices."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.input_combo.addItem(device['name'], i)
                if device['max_output_channels'] > 0:
                    self.output_combo.addItem(device['name'], i)
        except Exception as e:
            logger.error(f"Failed to load audio devices: {e}")
    
    def _test_microphone(self):
        """Test microphone input."""
        logger.info("Testing microphone...")
        # TODO: Implement microphone test
    
    def _test_speakers(self):
        """Test speaker output."""
        logger.info("Testing speakers...")
        # TODO: Implement speaker test


class WakeWordPage(QWizardPage):
    """Wake word calibration page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Wake Word")
        self.setSubTitle("Configure how Jarvis listens for your commands")
        
        layout = QVBoxLayout()
        
        # Enable wake word
        self.enable_checkbox = QCheckBox("Enable wake word detection (\"Hey Jarvis\")")
        self.enable_checkbox.setChecked(True)
        layout.addWidget(self.enable_checkbox)
        
        info_label = QLabel(
            "When enabled, Jarvis will listen for the wake word \"Hey Jarvis\" "
            "before processing commands. This saves battery and ensures privacy."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Sensitivity slider
        sensitivity_group = QGroupBox("Sensitivity")
        sensitivity_layout = QVBoxLayout()
        
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 100)
        self.sensitivity_slider.setValue(50)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setTickInterval(10)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Less sensitive"))
        slider_layout.addWidget(self.sensitivity_slider)
        slider_layout.addWidget(QLabel("More sensitive"))
        
        sensitivity_layout.addLayout(slider_layout)
        
        self.sensitivity_label = QLabel("Current: 50%")
        self.sensitivity_label.setAlignment(Qt.AlignCenter)
        sensitivity_layout.addWidget(self.sensitivity_label)
        
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(f"Current: {v}%")
        )
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Calibration button
        calibrate_btn = QPushButton("Calibrate Wake Word")
        calibrate_btn.clicked.connect(self._calibrate)
        layout.addWidget(calibrate_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _calibrate(self):
        """Calibrate wake word detection."""
        logger.info("Calibrating wake word...")
        # TODO: Implement wake word calibration


class STTTTSPage(QWizardPage):
    """Speech-to-text and text-to-speech selection page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Voice Processing")
        self.setSubTitle("Choose how Jarvis understands and speaks")
        
        layout = QVBoxLayout()
        
        # STT selection
        stt_group = QGroupBox("Speech-to-Text (STT)")
        stt_layout = QVBoxLayout()
        
        self.stt_offline = QRadioButton("Offline (Faster Whisper)")
        self.stt_offline.setChecked(True)
        stt_layout.addWidget(self.stt_offline)
        stt_layout.addWidget(QLabel("  ✓ Fast and private\n  ✓ No internet required\n  ✗ Less accurate"))
        
        stt_layout.addSpacing(10)
        
        self.stt_cloud = QRadioButton("Cloud (OpenAI)")
        stt_layout.addWidget(self.stt_cloud)
        stt_layout.addWidget(QLabel("  ✓ Very accurate\n  ✓ Real-time streaming\n  ✗ Requires internet and API key"))
        
        stt_group.setLayout(stt_layout)
        layout.addWidget(stt_group)
        
        # TTS selection
        tts_group = QGroupBox("Text-to-Speech (TTS)")
        tts_layout = QVBoxLayout()
        
        self.tts_offline = QRadioButton("Offline (Piper)")
        self.tts_offline.setChecked(True)
        tts_layout.addWidget(self.tts_offline)
        tts_layout.addWidget(QLabel("  ✓ Fast and private\n  ✓ No internet required\n  ✗ Robotic voice"))
        
        tts_layout.addSpacing(10)
        
        self.tts_cloud = QRadioButton("Cloud (Edge TTS)")
        tts_layout.addWidget(self.tts_cloud)
        tts_layout.addWidget(QLabel("  ✓ Natural voice\n  ✓ Multiple voices\n  ✗ Requires internet"))
        
        tts_group.setLayout(tts_layout)
        layout.addWidget(tts_group)
        
        # API key (for cloud)
        api_group = QGroupBox("OpenAI API Key (Optional)")
        api_layout = QVBoxLayout()
        
        api_layout.addWidget(QLabel("Enter your OpenAI API key for cloud STT:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        api_layout.addWidget(self.api_key_input)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        layout.addStretch()
        self.setLayout(layout)


class PrivacyPage(QWizardPage):
    """Privacy settings page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Privacy Settings")
        self.setSubTitle("Control what data Jarvis collects")
        
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Jarvis respects your privacy. All voice processing can be done offline, "
            "and no data is sent to third parties without your explicit consent."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Telemetry
        self.telemetry_checkbox = QCheckBox(
            "Send anonymous usage statistics (helps improve Jarvis)"
        )
        layout.addWidget(self.telemetry_checkbox)
        
        telemetry_info = QLabel(
            "  Includes: feature usage counts, performance metrics\n"
            "  Does NOT include: voice recordings, personal information"
        )
        telemetry_info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(telemetry_info)
        
        layout.addSpacing(10)
        
        # Crash reports
        self.crash_checkbox = QCheckBox(
            "Send crash reports (helps fix bugs)"
        )
        self.crash_checkbox.setChecked(True)
        layout.addWidget(self.crash_checkbox)
        
        crash_info = QLabel(
            "  Includes: error logs, system information\n"
            "  Does NOT include: voice recordings, personal information"
        )
        crash_info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(crash_info)
        
        layout.addStretch()
        self.setLayout(layout)


class IntegrationsPage(QWizardPage):
    """Optional integrations page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Optional Integrations")
        self.setSubTitle("Connect Jarvis to your accounts (optional)")
        
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "You can connect Jarvis to external services for enhanced functionality. "
            "All integrations are optional and can be configured later."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Google Calendar
        calendar_group = QGroupBox("Google Calendar")
        calendar_layout = QVBoxLayout()
        
        self.calendar_checkbox = QCheckBox("Enable Google Calendar integration")
        calendar_layout.addWidget(self.calendar_checkbox)
        
        calendar_info = QLabel(
            "Create and manage calendar events with voice commands.\n"
            "Requires: Google Calendar API credentials"
        )
        calendar_info.setWordWrap(True)
        calendar_layout.addWidget(calendar_info)
        
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)
        
        layout.addStretch()
        self.setLayout(layout)


class CompletionPage(QWizardPage):
    """Setup completion page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Setup Complete!")
        self.setSubTitle("You're ready to use Jarvis")
        
        layout = QVBoxLayout()
        
        # Success icon
        success_label = QLabel("✓")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("font-size: 72px; color: green;")
        layout.addWidget(success_label)
        
        # Summary
        summary = QLabel(
            "Jarvis is now configured and ready to use!\n\n"
            "Quick tips:\n"
            "• Say \"Hey Jarvis\" to activate voice commands\n"
            "• Try \"What's the time?\" or \"Set a reminder\"\n"
            "• Open settings to customize further\n\n"
            "Click Finish to start using Jarvis!"
        )
        summary.setAlignment(Qt.AlignCenter)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        
        # Launch checkbox
        self.launch_checkbox = QCheckBox("Launch Jarvis now")
        self.launch_checkbox.setChecked(True)
        self.launch_checkbox.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.launch_checkbox)
        
        layout.addStretch()
        self.setLayout(layout)


class FirstRunWizard(QWizard):
    """First-run setup wizard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Jarvis Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(700, 500)
        
        self.config = SetupConfig()
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.audio_page = AudioDevicePage()
        self.wakeword_page = WakeWordPage()
        self.stt_tts_page = STTTTSPage()
        self.privacy_page = PrivacyPage()
        self.integrations_page = IntegrationsPage()
        self.completion_page = CompletionPage()
        
        self.addPage(self.welcome_page)
        self.addPage(self.audio_page)
        self.addPage(self.wakeword_page)
        self.addPage(self.stt_tts_page)
        self.addPage(self.privacy_page)
        self.addPage(self.integrations_page)
        self.addPage(self.completion_page)
        
        # Connect finish signal
        self.finished.connect(self._on_finished)
    
    def _on_finished(self, result):
        """Handle wizard completion."""
        if result == QWizard.Accepted:
            logger.info("Setup wizard completed")
            self._collect_config()
            self._save_config()
    
    def _collect_config(self):
        """Collect configuration from wizard pages."""
        # Audio devices
        self.config.audio_input_device = self.audio_page.input_combo.currentData()
        self.config.audio_output_device = self.audio_page.output_combo.currentData()
        
        # Wake word
        self.config.wake_word_enabled = self.wakeword_page.enable_checkbox.isChecked()
        self.config.wake_word_sensitivity = self.wakeword_page.sensitivity_slider.value() / 100.0
        
        # STT/TTS
        self.config.stt_backend = "offline" if self.stt_tts_page.stt_offline.isChecked() else "cloud"
        self.config.tts_backend = "offline" if self.stt_tts_page.tts_offline.isChecked() else "cloud"
        self.config.openai_api_key = self.stt_tts_page.api_key_input.text() or None
        
        # Privacy
        self.config.telemetry_enabled = self.privacy_page.telemetry_checkbox.isChecked()
        self.config.crash_reports_enabled = self.privacy_page.crash_checkbox.isChecked()
        
        # Integrations
        self.config.google_calendar_enabled = self.integrations_page.calendar_checkbox.isChecked()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            config_manager = ConfigManager()
            
            # Update config
            if self.config.audio_input_device is not None:
                config_manager.set("audio.input_device_id", self.config.audio_input_device)
            if self.config.audio_output_device is not None:
                config_manager.set("audio.output_device_id", self.config.audio_output_device)
            
            config_manager.set("wake_word.enabled", self.config.wake_word_enabled)
            config_manager.set("wake_word.sensitivity", self.config.wake_word_sensitivity)
            
            config_manager.set("stt.backend", self.config.stt_backend)
            config_manager.set("tts.backend", self.config.tts_backend)
            
            if self.config.openai_api_key:
                # Store in secrets vault
                from core.secrets import SecretsVault
                vault = SecretsVault()
                vault.set_secret("openai_api_key", self.config.openai_api_key)
            
            config_manager.set("telemetry.enabled", self.config.telemetry_enabled)
            config_manager.set("crash_reports.enabled", self.config.crash_reports_enabled)
            
            # Mark first run as complete
            config_manager.set("first_run_complete", True)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")


def run_wizard():
    """Run the first-run wizard."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    wizard = FirstRunWizard()
    result = wizard.exec()
    
    return result == QWizard.Accepted


if __name__ == "__main__":
    success = run_wizard()
    sys.exit(0 if success else 1)

