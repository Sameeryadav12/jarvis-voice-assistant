"""
Barge-In: Interrupt TTS with Voice Detection

Detects voice during TTS playback and stops TTS to switch to listening mode.
"""

import sys
from pathlib import Path
from typing import Optional, Callable
from threading import Thread, Event, Lock
import numpy as np
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.audio.vad import SileroVAD


class BargeInDetector:
    """
    Detects voice input during TTS playback and triggers interruption.
    
    Features:
    - Continuous monitoring during TTS
    - Configurable sensitivity
    - Smooth interruption
    - Context preservation
    """
    
    def __init__(
        self,
        vad: Optional[SileroVAD] = None,
        sensitivity: float = 0.3,
        min_duration_ms: int = 200,
        sample_rate: int = 16000,
    ):
        """
        Initialize barge-in detector.
        
        Args:
            vad: VAD instance (auto-created if None)
            sensitivity: Detection sensitivity (0.0-1.0, lower = more sensitive)
            min_duration_ms: Minimum voice duration to trigger (ms)
            sample_rate: Audio sample rate
        """
        self.vad = vad
        if self.vad is None:
            from core.audio.vad import create_vad
            self.vad = create_vad()
        
        self.sensitivity = sensitivity
        self.min_duration_ms = min_duration_ms
        self.sample_rate = sample_rate
        
        # Adjust VAD threshold based on sensitivity
        # Lower sensitivity = lower threshold = more sensitive
        self.vad.threshold = max(0.1, min(0.9, 0.5 - (sensitivity * 0.4)))
        
        # State
        self.is_monitoring = False
        self.monitoring_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.lock = Lock()
        
        # Callbacks
        self.on_barge_in: Optional[Callable[[], None]] = None
        self.on_speech_start: Optional[Callable[[], None]] = None
        
        # Statistics
        self.detection_count = 0
        self.last_detection_time = 0.0
    
    def set_callbacks(
        self,
        on_barge_in: Optional[Callable[[], None]] = None,
        on_speech_start: Optional[Callable[[], None]] = None,
    ):
        """
        Set callbacks for barge-in events.
        
        Args:
            on_barge_in: Called when barge-in is detected (should stop TTS)
            on_speech_start: Called when speech start is detected
        """
        self.on_barge_in = on_barge_in
        self.on_speech_start = on_speech_start
    
    def start_monitoring(self, audio_callback: Callable[[], np.ndarray]):
        """
        Start monitoring for barge-in during TTS playback.
        
        Args:
            audio_callback: Function that returns current audio chunk
        """
        with self.lock:
            if self.is_monitoring:
                logger.warning("Barge-in monitoring already active")
                return
            
            logger.info("Starting barge-in monitoring")
            self.is_monitoring = True
            self.stop_event.clear()
            self.detection_count = 0
            
            # Start monitoring thread
            self.monitoring_thread = Thread(
                target=self._monitor_loop,
                args=(audio_callback,),
                daemon=True,
            )
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring for barge-in."""
        with self.lock:
            if not self.is_monitoring:
                return
            
            logger.info("Stopping barge-in monitoring")
            self.is_monitoring = False
            self.stop_event.set()
            
            # Wait for thread
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=1.0)
    
    def _monitor_loop(self, audio_callback: Callable[[], np.ndarray]):
        """Monitor loop running in background thread."""
        logger.debug("Barge-in monitoring thread started")
        
        voice_duration_ms = 0
        min_duration_samples = int((self.min_duration_ms / 1000.0) * self.sample_rate)
        samples_per_chunk = int((30 / 1000.0) * self.sample_rate)  # 30ms chunks
        
        try:
            while self.is_monitoring and not self.stop_event.is_set():
                # Get audio chunk
                try:
                    audio_chunk = audio_callback()
                except Exception as e:
                    logger.error(f"Error getting audio chunk: {e}")
                    break
                
                if audio_chunk is None or len(audio_chunk) == 0:
                    continue
                
                # Ensure correct size
                if len(audio_chunk) < 512:  # VAD requires at least 512 samples
                    # Pad or skip
                    continue
                
                # Process with VAD
                is_speech = self.vad.process_chunk(audio_chunk, self.sample_rate)
                
                if is_speech:
                    voice_duration_ms += (len(audio_chunk) / self.sample_rate) * 1000
                    
                    # Emit speech start callback
                    if self.on_speech_start and voice_duration_ms < 100:
                        # Only call once at start
                        try:
                            self.on_speech_start()
                        except Exception as e:
                            logger.error(f"Error in on_speech_start callback: {e}")
                    
                    # Check if duration threshold met
                    if voice_duration_ms >= self.min_duration_ms:
                        logger.info(f"Barge-in detected! Voice duration: {voice_duration_ms:.0f}ms")
                        
                        self.detection_count += 1
                        import time
                        self.last_detection_time = time.time()
                        
                        # Trigger barge-in callback
                        if self.on_barge_in:
                            try:
                                self.on_barge_in()
                            except Exception as e:
                                logger.error(f"Error in on_barge_in callback: {e}")
                        
                        # Reset counter
                        voice_duration_ms = 0
                else:
                    # Reset if silence
                    voice_duration_ms = 0
                
                # Small delay to avoid CPU spinning
                import time
                time.sleep(0.01)  # 10ms
        
        except Exception as e:
            logger.error(f"Error in barge-in monitoring loop: {e}")
        finally:
            logger.debug("Barge-in monitoring thread stopped")
    
    def get_stats(self) -> dict:
        """Get barge-in detection statistics."""
        return {
            "detection_count": self.detection_count,
            "last_detection_time": self.last_detection_time,
            "is_monitoring": self.is_monitoring,
            "sensitivity": self.sensitivity,
        }


class TTSBargeInManager:
    """
    Manages TTS playback with barge-in support.
    
    Coordinates TTS playback and barge-in detection.
    """
    
    def __init__(
        self,
        tts_player,  # TTS player instance (e.g., edge-tts, piper)
        barge_in_detector: Optional[BargeInDetector] = None,
    ):
        """
        Initialize TTS barge-in manager.
        
        Args:
            tts_player: TTS player instance with play/stop methods
            barge_in_detector: Barge-in detector (auto-created if None)
        """
        self.tts_player = tts_player
        self.barge_in_detector = barge_in_detector
        
        if self.barge_in_detector is None:
            self.barge_in_detector = BargeInDetector()
        
        # Set up barge-in callback
        self.barge_in_detector.set_callbacks(
            on_barge_in=self._handle_barge_in,
        )
        
        # State
        self.is_playing = False
        self.was_interrupted = False
    
    def speak(
        self,
        text: str,
        audio_callback: Callable[[], np.ndarray],
        **tts_kwargs,
    ) -> bool:
        """
        Speak text with barge-in support.
        
        Args:
            text: Text to speak
            audio_callback: Audio callback for barge-in detection
            **tts_kwargs: Additional arguments for TTS player
            
        Returns:
            True if completed, False if interrupted
        """
        self.is_playing = True
        self.was_interrupted = False
        
        logger.info(f"Speaking: {text[:50]}...")
        
        # Start barge-in monitoring
        self.barge_in_detector.start_monitoring(audio_callback)
        
        try:
            # Play TTS (this should be non-blocking or run in thread)
            self.tts_player.speak(text, **tts_kwargs)
            
            # Wait for completion or interruption
            # (Implementation depends on TTS player)
            while self.is_playing:
                import time
                time.sleep(0.1)
                
                if self.was_interrupted:
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error during TTS playback: {e}")
            return False
        
        finally:
            # Stop monitoring
            self.barge_in_detector.stop_monitoring()
            self.is_playing = False
    
    def _handle_barge_in(self):
        """Handle barge-in detection."""
        logger.info("Barge-in detected during TTS playback")
        self.was_interrupted = True
        
        # Stop TTS
        if hasattr(self.tts_player, 'stop'):
            try:
                self.tts_player.stop()
            except Exception as e:
                logger.error(f"Error stopping TTS: {e}")
        
        # Stop playback flag
        self.is_playing = False
    
    def stop(self):
        """Stop TTS playback."""
        if self.is_playing:
            logger.info("Stopping TTS playback")
            self.is_playing = False
            
            if hasattr(self.tts_player, 'stop'):
                try:
                    self.tts_player.stop()
                except Exception as e:
                    logger.error(f"Error stopping TTS: {e}")
            
            self.barge_in_detector.stop_monitoring()
    
    def was_interrupted(self) -> bool:
        """Check if last speak() was interrupted."""
        return self.was_interrupted


def create_barge_in_detector(
    sensitivity: float = 0.3,
    vad: Optional[SileroVAD] = None,
) -> BargeInDetector:
    """
    Create a barge-in detector with default settings.
    
    Args:
        sensitivity: Detection sensitivity (0.0-1.0)
        vad: Optional VAD instance
        
    Returns:
        BargeInDetector instance
    """
    return BargeInDetector(vad=vad, sensitivity=sensitivity)

