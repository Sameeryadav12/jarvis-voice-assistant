"""
Python-QML Bridge for Jarvis Desktop UI
Connects QML components to Jarvis backend functionality.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtQml import qmlRegisterType
import sys
from pathlib import Path
import logging
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class JarvisBridge(QObject):
    """Bridge between QML UI and Python backend."""
    
    # Signals to QML
    audioAmplitudeChanged = Signal(float)
    orbStateChanged = Signal(str)
    statusTextChanged = Signal(str)
    partialTranscriptChanged = Signal(str)
    committedTranscriptChanged = Signal(str)
    activityAdded = Signal(dict)  # Activity card data
    activityHistoryChanged = Signal()  # Notify when history changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._audio_amplitude = 0.0
        self._orb_state = "idle"
        self._status_text = "Ready"
        self._partial_transcript = ""
        self._committed_transcript = ""
        self._activity_history = []
        
        # Initialize Jarvis components
        self.init_jarvis()
    
    def init_jarvis(self):
        """Initialize Jarvis backend components."""
        try:
            from core.nlu.intents import IntentClassifier, IntentType
            from core.nlu.router import CommandRouter
            from core.skills.information import InformationSkills
            from core.skills.system import SystemSkills
            from core.skills.reminders import ReminderSkills
            
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
            
            logger.info("Jarvis backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Jarvis: {e}")
            self.classifier = None
            self.router = None
    
    # Properties for QML binding
    @Property(float, notify=audioAmplitudeChanged)
    def audioAmplitude(self):
        return self._audio_amplitude
    
    @audioAmplitude.setter
    def audioAmplitude(self, value):
        if self._audio_amplitude != value:
            self._audio_amplitude = value
            self.audioAmplitudeChanged.emit(value)
    
    @Property(str, notify=orbStateChanged)
    def orbState(self):
        return self._orb_state
    
    @orbState.setter
    def orbState(self, value):
        if self._orb_state != value:
            self._orb_state = value
            self.orbStateChanged.emit(value)
    
    @Property(str, notify=statusTextChanged)
    def statusText(self):
        return self._status_text
    
    @statusText.setter
    def statusText(self, value):
        if self._status_text != value:
            self._status_text = value
            self.statusTextChanged.emit(value)
    
    @Property(list, notify=activityHistoryChanged)
    def activityHistory(self):
        return self._activity_history
    
    # Slots (callable from QML)
    @Slot(str)
    def executeCommand(self, command: str):
        """Execute a command from QML."""
        if not self.router or not self.classifier:
            logger.warning("Jarvis not initialized")
            return
        
        logger.info(f"Executing command: {command}")
        self.orbState = "processing"
        self.statusText = "Processing..."
        
        try:
            # Classify intent
            intent = self.classifier.classify(command)
            
            # Route to handler
            import asyncio
            result = asyncio.run(self.router.route(intent))
            
            # Add to activity history
            activity = {
                "intentName": intent.type.name if intent.type else "Unknown",
                "intentIcon": self.getIntentIcon(intent.type.name if intent.type else ""),
                "timestamp": datetime.now().strftime("%H:%M"),
                "userCommand": command,
                "jarvisResponse": result.message if result else "No response",
                "isPinned": False
            }
            self._activity_history.insert(0, activity)  # Add to beginning
            self.activityAdded.emit(activity)
            self.activityHistoryChanged.emit()  # Notify QML
            
            self.orbState = "idle"
            self.statusText = "Ready"
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self.orbState = "idle"
            self.statusText = f"Error: {str(e)}"
    
    @Slot()
    def activateVoice(self):
        """Activate voice listening."""
        logger.info("Voice activated")
        self.orbState = "listening"
        self.statusText = "Listening..."
        # TODO: Connect to audio pipeline
    
    @Slot()
    def deactivateVoice(self):
        """Deactivate voice listening."""
        logger.info("Voice deactivated")
        self.orbState = "idle"
        self.statusText = "Ready"
    
    @Slot(float)
    def updateAudioAmplitude(self, amplitude: float):
        """Update audio amplitude from audio pipeline."""
        self.audioAmplitude = min(1.0, max(0.0, amplitude))
    
    @Slot(str)
    def updatePartialTranscript(self, text: str):
        """Update partial transcript from STT."""
        self._partial_transcript = text
        self.partialTranscriptChanged.emit(text)
    
    @Slot(str)
    def updateCommittedTranscript(self, text: str):
        """Update committed transcript."""
        self._committed_transcript = text
        self.committedTranscriptChanged.emit(text)
    
    def getIntentIcon(self, intent_name: str):
        """Get icon for intent type."""
        icons = {
            "GET_TIME": "🕒",
            "GET_DATE": "📅",
            "GET_BATTERY": "🔋",
            "GET_SYSTEM_INFO": "💻",
            "SET_TIMER": "⏱️",
            "CREATE_REMINDER": "📝",
            "HELP": "❓",
            "VOLUME_UP": "🔊",
            "VOLUME_DOWN": "🔉",
            "VOLUME_SET": "🎚️",
            "MUTE": "🔇",
            "UNMUTE": "🔊"
        }
        return icons.get(intent_name, "💬")
    
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'reminder_skills'):
            self.reminder_skills.shutdown()


# Register type for QML
def register_bridge():
    """Register JarvisBridge for use in QML."""
    qmlRegisterType(JarvisBridge, "com.jarvis.bridge", 1, 0, "JarvisBridge")

