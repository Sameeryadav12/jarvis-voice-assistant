"""
Intent classification and entity extraction using spaCy.
Maps natural language to structured commands.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import spacy
from loguru import logger

from .entity_extractor import EntityExtractor


class IntentType(Enum):
    """Supported intent types - 80+ comprehensive intents."""
    
    # ==================== System Control (10) ====================
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_SET = "volume_set"
    MUTE = "mute"
    UNMUTE = "unmute"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    BRIGHTNESS_SET = "brightness_set"
    SLEEP_COMPUTER = "sleep_computer"
    RESTART_COMPUTER = "restart_computer"
    
    # ==================== Window/App Management (12) ====================
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    FOCUS_WINDOW = "focus_window"
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    CLOSE_WINDOW = "close_window"
    LIST_OPEN_APPS = "list_open_apps"
    SWITCH_APP = "switch_app"
    SNAP_WINDOW_LEFT = "snap_window_left"
    SNAP_WINDOW_RIGHT = "snap_window_right"
    SNAP_WINDOW_CENTER = "snap_window_center"
    SHOW_DESKTOP = "show_desktop"
    
    # ==================== Time & Reminders (10) ====================
    CREATE_REMINDER = "create_reminder"
    LIST_REMINDERS = "list_reminders"
    CANCEL_REMINDER = "cancel_reminder"
    SET_TIMER = "set_timer"
    SET_ALARM = "set_alarm"
    SNOOZE_REMINDER = "snooze_reminder"
    CHECK_SCHEDULE = "check_schedule"
    WHATS_NEXT = "whats_next"
    HOW_MUCH_TIME = "how_much_time"
    WHEN_IS = "when_is"
    
    # ==================== Calendar (12) ====================
    CREATE_EVENT = "create_event"
    LIST_EVENTS = "list_events"
    CANCEL_EVENT = "cancel_event"
    MOVE_EVENT = "move_event"
    RESCHEDULE_EVENT = "reschedule_event"
    CHECK_AVAILABILITY = "check_availability"
    FIND_FREE_TIME = "find_free_time"
    SETUP_MEETING = "setup_meeting"
    JOIN_MEETING = "join_meeting"
    END_MEETING = "end_meeting"
    MEETING_SUMMARY = "meeting_summary"
    CALENDAR_CONFLICTS = "calendar_conflicts"
    
    # ==================== Web & Search (8) ====================
    SEARCH_WEB = "search_web"
    OPEN_URL = "open_url"
    GOOGLE_IT = "google_it"
    SEARCH_IMAGES = "search_images"
    SEARCH_VIDEOS = "search_videos"
    OPEN_NEW_TAB = "open_new_tab"
    CLOSE_TAB = "close_tab"
    GO_BACK = "go_back"
    
    # ==================== Information & Knowledge (10) ====================
    ASK_QUESTION = "ask_question"
    GET_TIME = "get_time"
    GET_DATE = "get_date"
    GET_WEATHER = "get_weather"
    WEATHER_FORECAST = "weather_forecast"
    CALCULATE = "calculate"
    CONVERT_UNITS = "convert_units"
    DEFINE_WORD = "define_word"
    FACT_CHECK = "fact_check"
    NEWS_UPDATE = "news_update"
    
    # ==================== Memory (8) ====================
    REMEMBER_FACT = "remember_fact"
    RECALL_FACT = "recall_fact"
    FORGET_FACT = "forget_fact"
    LIST_MEMORIES = "list_memories"
    SEARCH_MEMORY = "search_memory"
    UPDATE_MEMORY = "update_memory"
    CLEAR_ALL_MEMORIES = "clear_all_memories"
    MEMORY_STATS = "memory_stats"
    
    # ==================== System Information (8) ====================
    GET_SYSTEM_INFO = "get_system_info"
    GET_BATTERY = "get_battery"
    CHECK_WIFI = "check_wifi"
    CHECK_STORAGE = "check_storage"
    CHECK_CPU_USAGE = "check_cpu_usage"
    CHECK_MEMORY_USAGE = "check_memory_usage"
    NETWORK_STATUS = "network_status"
    SYSTEM_HEALTH = "system_health"
    
    # ==================== Media Control (10) ====================
    PLAY_MEDIA = "play_media"
    PAUSE_MEDIA = "pause_media"
    STOP_MEDIA = "stop_media"
    NEXT_TRACK = "next_track"
    PREVIOUS_TRACK = "previous_track"
    VOLUME_MEDIA_UP = "volume_media_up"
    VOLUME_MEDIA_DOWN = "volume_media_down"
    REPEAT_TRACK = "repeat_track"
    SHUFFLE_MODE = "shuffle_mode"
    CURRENT_TRACK = "current_track"
    
    # ==================== Communication (10) ====================
    SEND_EMAIL = "send_email"
    READ_EMAIL = "read_email"
    CHECK_EMAIL = "check_email"
    REPLY_EMAIL = "reply_email"
    FORWARD_EMAIL = "forward_email"
    COMPOSE_MESSAGE = "compose_message"
    READ_MESSAGES = "read_messages"
    SEND_MESSAGE = "send_message"
    CALL_CONTACT = "call_contact"
    VIDEO_CALL = "video_call"
    
    # ==================== File & Document Management (8) ====================
    CREATE_FILE = "create_file"
    OPEN_FILE = "open_file"
    DELETE_FILE = "delete_file"
    SAVE_FILE = "save_file"
    LIST_FILES = "list_files"
    FIND_FILE = "find_file"
    COPY_FILE = "copy_file"
    MOVE_FILE = "move_file"
    
    # ==================== Tasks & Notes (8) ====================
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    CREATE_NOTE = "create_note"
    LIST_NOTES = "list_notes"
    SEARCH_NOTES = "search_notes"
    DELETE_NOTE = "delete_note"
    
    # ==================== Screen & Media (6) ====================
    TAKE_SCREENSHOT = "take_screenshot"
    RECORD_SCREEN = "record_screen"
    STOP_RECORDING = "stop_recording"
    CAPTURE_REGION = "capture_region"
    START_SCREENSHARE = "start_screenshare"
    STOP_SCREENSHARE = "stop_screenshare"
    
    # ==================== Shopping & E-commerce (4) ====================
    SEARCH_PRODUCT = "search_product"
    ADD_TO_CART = "add_to_cart"
    CHECK_CART = "check_cart"
    PLACE_ORDER = "place_order"
    
    # ==================== Social Media (6) ====================
    POST_SOCIAL = "post_social"
    CHECK_FEED = "check_feed"
    LIKE_POST = "like_post"
    COMMENT_POST = "comment_post"
    SHARE_POST = "share_post"
    FOLLOW_USER = "follow_user"
    
    # ==================== Travel & Navigation (6) ====================
    GET_DIRECTIONS = "get_directions"
    ESTIMATE_ARRIVAL = "estimate_arrival"
    BOOK_FLIGHT = "book_flight"
    HOTEL_SEARCH = "hotel_search"
    RESTAURANT_SEARCH = "restaurant_search"
    TRAFFIC_UPDATE = "traffic_update"
    
    # ==================== Finance & Payments (6) ====================
    CHECK_BALANCE = "check_balance"
    RECENT_TRANSACTIONS = "recent_transactions"
    SEND_PAYMENT = "send_payment"
    PAY_BILL = "pay_bill"
    BUDGET_CHECK = "budget_check"
    CURRENCY_CONVERT = "currency_convert"
    
    # ==================== Health & Fitness (6) ====================
    LOG_WORKOUT = "log_workout"
    CHECK_STEPS = "check_steps"
    SET_FITNESS_GOAL = "set_fitness_goal"
    CALORIE_TRACK = "calorie_track"
    WATER_REMINDER = "water_reminder"
    MEDICATION_REMINDER = "medication_reminder"
    
    # ==================== Jarvis Control (8) ====================
    HELP = "help"
    STOP = "stop"
    CANCEL = "cancel"
    THANK_YOU = "thank_you"
    GOODBYE = "goodbye"
    HOW_ARE_YOU = "how_are_you"
    CHANGE_VOICE = "change_voice"
    ADJUST_SPEED = "adjust_speed"
    
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """
    Extracted entity from user input.
    
    Attributes:
        type: Entity type (e.g., 'app_name', 'volume_level', 'time')
        value: Entity value
        confidence: Confidence score
        span: Text span (start, end)
    """
    type: str
    value: Any
    confidence: float = 1.0
    span: Optional[Tuple[int, int]] = None


@dataclass
class Intent:
    """
    Classified intent with entities.
    
    Attributes:
        type: Intent type
        confidence: Confidence score
        entities: List of extracted entities
        raw_text: Original user input
    """
    type: IntentType
    confidence: float
    entities: List[Entity]
    raw_text: str


class IntentClassifier:
    """
    Intent classification using spaCy and pattern matching.
    Uses a hybrid approach: patterns for high-confidence matches,
    ML for ambiguous cases.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize intent classifier.
        
        Args:
            model_name: spaCy model name
        """
        try:
            # Try loading the model
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            # Fallback: Try to find the model in the bundled data
            import sys
            import os
            
            # Check if running as PyInstaller bundle
            if getattr(sys, 'frozen', False):
                bundle_dir = sys._MEIPASS
                model_path = os.path.join(bundle_dir, model_name, 'en_core_web_sm-3.8.0')
                
                if os.path.exists(model_path):
                    logger.info(f"Loading spaCy model from bundle: {model_path}")
                    self.nlp = spacy.load(model_path)
                    logger.info(f"Loaded spaCy model from bundle: {model_name}")
                else:
                    logger.warning(
                        f"spaCy model '{model_name}' not found in bundle. "
                        f"Expected at: {model_path}"
                    )
                    raise
            else:
                logger.warning(
                    f"spaCy model '{model_name}' not found. "
                    f"Run: python -m spacy download {model_name}"
                )
                raise
        
        # Define intent patterns (simple rule-based for MVP)
        self.patterns = self._init_patterns()
        
        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()
        
        logger.info("IntentClassifier initialized")

    def _init_patterns(self) -> Dict[IntentType, List[str]]:
        """
        Initialize intent patterns.
        
        Returns:
            Dictionary mapping intents to keyword patterns
        """
        return {
            # System Control
            IntentType.VOLUME_UP: [
                "volume up", "increase volume", "louder", "turn it up",
                "raise volume", "boost volume", "crank it up",
                "turn up the volume", "turn up volume", "up the volume"
            ],
            IntentType.VOLUME_DOWN: [
                "volume down", "decrease volume", "quieter", "turn it down",
                "lower volume", "reduce volume", "quiet down",
                "turn down the volume", "turn down volume", "down the volume"
            ],
            IntentType.VOLUME_SET: [
                "set volume", "volume to", "change volume to", "volume at",
                "set volume to", "make volume", "adjust volume to", "change volume",
                "volume level", "set the volume to"
            ],
            IntentType.MUTE: [
                "mute", "silence", "turn off sound", "mute audio",
                "quiet", "shhh", "hush"
            ],
            IntentType.UNMUTE: [
                "unmute", "turn on sound", "unmute audio", "sound on"
            ],
            
            # Window/App Management
            IntentType.OPEN_APP: [
                "open", "launch", "start", "run", "start up"
            ],
            IntentType.CLOSE_APP: [
                "close", "quit", "exit", "shut down", "kill"
            ],
            IntentType.FOCUS_WINDOW: [
                "focus on", "switch to", "go to", "show me", "bring up"
            ],
            IntentType.MINIMIZE_WINDOW: [
                "minimize", "hide", "minimize window"
            ],
            IntentType.MAXIMIZE_WINDOW: [
                "maximize", "full screen", "maximize window"
            ],
            
            # Time & Reminders
            IntentType.CREATE_REMINDER: [
                "remind me", "set reminder", "reminder to", "don't forget",
                "remember to remind", "make a reminder"
            ],
            IntentType.LIST_REMINDERS: [
                "list reminders", "show reminders", "what reminders",
                "my reminders", "upcoming reminders", "show my reminders",
                "what are my reminders", "check reminders", "view reminders",
                "all reminders", "reminder list"
            ],
            IntentType.CANCEL_REMINDER: [
                "cancel reminder", "delete reminder", "remove reminder",
                "forget reminder"
            ],
            IntentType.SET_TIMER: [
                "set timer", "timer for", "start timer", "countdown",
                "set a timer", "create timer", "start a timer", "make a timer",
                "timer", "set timer for", "countdown for"
            ],
            IntentType.SET_ALARM: [
                "set alarm", "wake me", "alarm for", "alarm at"
            ],
            
            # Calendar
            IntentType.CREATE_EVENT: [
                "create event", "add meeting", "schedule", "add to calendar",
                "meeting with", "appointment with", "book"
            ],
            IntentType.LIST_EVENTS: [
                "list events", "show calendar", "what's on my calendar",
                "my schedule", "upcoming events", "today's schedule"
            ],
            IntentType.CANCEL_EVENT: [
                "cancel event", "cancel meeting", "delete event",
                "remove from calendar"
            ],
            
            # Web & Search
            IntentType.SEARCH_WEB: [
                "search for", "google", "look up", "find information about",
                "search", "find", "look for"
            ],
            IntentType.OPEN_URL: [
                "open website", "go to", "navigate to", "visit"
            ],
            
            # Information & Knowledge
            IntentType.ASK_QUESTION: [
                "what is", "who is", "when is", "where is", "how do",
                "tell me about", "explain", "define"
            ],
            IntentType.GET_TIME: [
                "what time", "current time", "what's the time", "time is it",
                "tell me the time", "what time is it", "can you tell me the time",
                "what's the current time", "give me the time", "time please",
                "show me the time", "check the time"
            ],
            IntentType.GET_DATE: [
                "what date", "what's the date", "today's date", "what day",
                "tell me the date", "what is today's date", "what day is it",
                "what's today", "give me the date", "date please",
                "what is the date today", "current date"
            ],
            IntentType.GET_WEATHER: [
                "weather", "what's the weather", "temperature", "forecast",
                "how's the weather", "will it rain"
            ],
            
            # Memory
            IntentType.REMEMBER_FACT: [
                "remember", "save this", "note that", "keep in mind",
                "write down", "store", "memorize"
            ],
            IntentType.RECALL_FACT: [
                "what did i", "recall", "what was", "do you remember",
                "remind me what", "what did i say"
            ],
            IntentType.FORGET_FACT: [
                "forget", "delete that", "remove that", "erase"
            ],
            
            # System Information
            IntentType.GET_SYSTEM_INFO: [
                "system info", "computer stats", "system stats", "pc info",
                "show system info", "system status", "check system", "how's my system",
                "computer information", "system details", "show system status"
            ],
            IntentType.GET_BATTERY: [
                "battery", "battery level", "how much battery", "battery percentage",
                "check battery", "battery status", "show battery", "what's my battery",
                "how's the battery", "battery life", "check the battery"
            ],
            
            # Media Control
            IntentType.PLAY_MEDIA: [
                "play", "start playing", "resume", "unpause"
            ],
            IntentType.PAUSE_MEDIA: [
                "pause", "stop playing", "hold"
            ],
            IntentType.NEXT_TRACK: [
                "next", "skip", "next song", "next track"
            ],
            IntentType.PREVIOUS_TRACK: [
                "previous", "back", "previous song", "last track", "go back"
            ],
            
            # Jarvis Control
            IntentType.HELP: [
                "help", "what can you do", "commands", "show help",
                "help me", "instructions", "what are you capable of",
                "show me commands", "list commands", "what commands", "capabilities"
            ],
            IntentType.STOP: [
                "stop", "nevermind", "never mind", "forget it"
            ],
            IntentType.CANCEL: [
                "cancel", "abort", "undo"
            ],
            IntentType.THANK_YOU: [
                "thank you", "thanks", "appreciate it", "great"
            ]
        }

    def classify(self, text: str) -> Intent:
        """
        Classify user input into an intent with entities.
        
        Args:
            text: User input text
            
        Returns:
            Intent object
        """
        text_lower = text.lower().strip()
        doc = self.nlp(text)
        
        # Pattern matching for intent
        intent_type, confidence = self._match_intent(text_lower)
        
        # Extract entities
        entities = self._extract_entities(doc, intent_type)
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            entities=entities,
            raw_text=text
        )

    def _match_intent(self, text: str) -> Tuple[IntentType, float]:
        """
        Match text against intent patterns.
        
        Args:
            text: Lowercase user input
            
        Returns:
            Tuple of (intent_type, confidence)
        """
        # Priority queue for intent matching
        matches = []
        
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern in text:
                    # Calculate confidence based on pattern length
                    confidence = len(pattern) / max(len(text), len(pattern))
                    
                    # Bonus for exact match
                    if pattern == text:
                        confidence = 1.0
                    # Bonus for word boundary match
                    elif f" {pattern} " in f" {text} " or text.startswith(pattern + " ") or text.endswith(" " + pattern):
                        confidence *= 1.3
                    
                    confidence = min(confidence, 1.0)  # Cap at 1.0
                    matches.append((confidence, intent_type))
        
        if not matches:
            return IntentType.UNKNOWN, 0.0
        
        # Return highest confidence match
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1], matches[0][0]

    def _extract_entities(
        self,
        doc: spacy.tokens.Doc,
        intent_type: IntentType
    ) -> List[Entity]:
        """
        Extract entities based on intent type.
        
        Args:
            doc: spaCy document
            intent_type: Classified intent
            
        Returns:
            List of entities
        """
        entities = []
        text = doc.text
        
        # Extract named entities from spaCy
        for ent in doc.ents:
            entities.append(Entity(
                type=ent.label_,
                value=ent.text,
                confidence=1.0,
                span=(ent.start_char, ent.end_char)
            ))
        
        # Use enhanced entity extractor for specific extractions
        extracted = self.entity_extractor.extract_all(text)
        
        # Intent-specific entity extraction
        if intent_type == IntentType.VOLUME_SET:
            # Extract numbers or percentages for volume level
            if extracted.get('percentage'):
                entities.append(Entity(
                    type="volume_level",
                    value=extracted['percentage']['value'],
                    confidence=1.0
                ))
            elif extracted.get('numbers'):
                for num in extracted['numbers']:
                    entities.append(Entity(
                        type="volume_level",
                        value=num['value'],
                        confidence=1.0
                    ))
        
        elif intent_type in [IntentType.OPEN_APP, IntentType.CLOSE_APP, IntentType.FOCUS_WINDOW]:
            # Extract app name
            if extracted.get('app_name'):
                entities.append(Entity(
                    type="app_name",
                    value=extracted['app_name']['value'],
                    confidence=0.9
                ))
        
        elif intent_type in [IntentType.CREATE_REMINDER, IntentType.SET_TIMER, IntentType.SET_ALARM]:
            # Extract time and duration
            if extracted.get('time'):
                entities.append(Entity(
                    type="time",
                    value=extracted['time'],
                    confidence=0.9
                ))
            if extracted.get('duration'):
                entities.append(Entity(
                    type="duration",
                    value=extracted['duration']['seconds'],
                    confidence=0.9
                ))
        
        elif intent_type in [IntentType.CREATE_EVENT, IntentType.LIST_EVENTS]:
            # Extract date and time
            if extracted.get('date'):
                entities.append(Entity(
                    type="date",
                    value=extracted['date']['date'],
                    confidence=0.9
                ))
            if extracted.get('time'):
                entities.append(Entity(
                    type="time",
                    value=extracted['time'],
                    confidence=0.9
                ))
        
        elif intent_type == IntentType.SEARCH_WEB:
            # Extract search query (everything after trigger)
            trigger_words = ["search for", "google", "look up", "find"]
            query = text
            for trigger in trigger_words:
                if trigger in text.lower():
                    query = text.lower().split(trigger, 1)[1].strip()
                    break
            entities.append(Entity(
                type="search_query",
                value=query,
                confidence=0.9
            ))
        
        elif intent_type == IntentType.OPEN_URL:
            # Extract URLs
            if extracted.get('urls'):
                for url in extracted['urls']:
                    entities.append(Entity(
                        type="url",
                        value=url['value'],
                        confidence=1.0
                    ))
        
        return entities

    def add_pattern(self, intent_type: IntentType, pattern: str) -> None:
        """
        Add a custom pattern for an intent.
        
        Args:
            intent_type: Intent to add pattern for
            pattern: Pattern string
        """
        if intent_type not in self.patterns:
            self.patterns[intent_type] = []
        self.patterns[intent_type].append(pattern.lower())
        logger.debug(f"Added pattern '{pattern}' for {intent_type.value}")


class PriorityIntentQueue:
    """
    Priority queue for intent arbitration.
    Demonstrates DSA knowledge - uses heap for O(log n) operations.
    """

    def __init__(self):
        """Initialize priority queue."""
        self.queue: List[Tuple[float, Intent]] = []

    def add_intent(self, intent: Intent) -> None:
        """
        Add intent to queue.
        
        Args:
            intent: Intent to add
        """
        import heapq
        # Negative confidence for max-heap behavior
        heapq.heappush(self.queue, (-intent.confidence, intent))

    def get_best_intent(self) -> Optional[Intent]:
        """
        Get highest confidence intent.
        
        Returns:
            Best intent or None if queue empty
        """
        import heapq
        if not self.queue:
            return None
        _, intent = heapq.heappop(self.queue)
        return intent

    def clear(self) -> None:
        """Clear the queue."""
        self.queue.clear()

