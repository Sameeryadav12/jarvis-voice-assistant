"""
Audio pipeline integrating capture, wake word detection, and STT.
Coordinates the full voice input flow.
"""

import asyncio
import threading
from typing import Optional, Callable, List
from enum import Enum
import numpy as np
from loguru import logger

from .capture import AudioCapture
from .wakeword import WakeWordDetector
from .stt_offline import WhisperSTT
from .stt_realtime import RealtimeSTT


class PipelineState(Enum):
    """Audio pipeline states."""
    STOPPED = "stopped"
    LISTENING = "listening"
    WAKE_WORD_DETECTED = "wake_word_detected"
    PROCESSING_SPEECH = "processing_speech"
    ERROR = "error"


class AudioPipeline:
    """
    Complete audio pipeline: capture → wake word → STT → callback.
    
    This class orchestrates the entire voice input flow:
    1. Continuously capture audio
    2. Detect wake word
    3. Capture speech after wake word
    4. Transcribe speech
    5. Call user callback with transcript
    """

    def __init__(
        self,
        stt_mode: str = "offline",
        wake_word_config: Optional[dict] = None,
        stt_config: Optional[dict] = None,
        on_transcript: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[PipelineState], None]] = None
    ):
        """
        Initialize audio pipeline.
        
        Args:
            stt_mode: 'offline' (whisper.cpp) or 'cloud' (OpenAI Realtime)
            wake_word_config: Wake word detector configuration
            stt_config: STT configuration
            on_transcript: Callback when transcript ready
            on_state_change: Callback when pipeline state changes
        """
        self.stt_mode = stt_mode
        self.on_transcript = on_transcript
        self.on_state_change = on_state_change
        
        # State
        self.state = PipelineState.STOPPED
        self.running = False
        
        # Components
        self.audio_capture: Optional[AudioCapture] = None
        self.wake_word_detector: Optional[WakeWordDetector] = None
        self.stt_offline: Optional[WhisperSTT] = None
        self.stt_cloud: Optional[RealtimeSTT] = None
        
        # Configuration
        self.wake_word_config = wake_word_config or {}
        self.stt_config = stt_config or {}
        
        # Speech capture buffer (after wake word)
        self.speech_buffer: List[np.ndarray] = []
        self.capturing_speech = False
        self.speech_timeout = 3.0  # seconds of silence before processing
        self.silence_threshold = 0.01  # RMS threshold for silence detection
        self.silence_duration = 0.0
        
        logger.info(f"AudioPipeline initialized: mode={stt_mode}")

    def _set_state(self, new_state: PipelineState) -> None:
        """
        Update pipeline state and notify callback.
        
        Args:
            new_state: New state
        """
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            logger.info(f"Pipeline state: {old_state.value} → {new_state.value}")
            
            if self.on_state_change:
                try:
                    self.on_state_change(new_state)
                except Exception as e:
                    logger.error(f"Error in state change callback: {e}")

    def _on_wake_word_detected(self, keyword_index: int) -> None:
        """
        Callback when wake word detected.
        
        Args:
            keyword_index: Index of detected keyword
        """
        logger.info("Wake word detected!")
        self._set_state(PipelineState.WAKE_WORD_DETECTED)
        
        # Start capturing speech
        self.capturing_speech = True
        self.speech_buffer.clear()
        self.silence_duration = 0.0
        
        self._set_state(PipelineState.PROCESSING_SPEECH)

    def _on_audio_frame(self, audio_data: np.ndarray) -> None:
        """
        Callback for each audio frame from capture.
        
        Args:
            audio_data: Audio frame
        """
        # Process wake word detection
        if self.wake_word_detector and not self.capturing_speech:
            try:
                # Convert to int16 for Porcupine
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                # Process frame (needs to match wake word frame length)
                frame_length = self.wake_word_detector.frame_length
                
                # Process in chunks of frame_length
                for i in range(0, len(audio_int16), frame_length):
                    frame = audio_int16[i:i + frame_length]
                    if len(frame) == frame_length:
                        self.wake_word_detector.process_frame(frame)
            except Exception as e:
                logger.error(f"Wake word processing error: {e}")
        
        # Capture speech after wake word
        if self.capturing_speech:
            self.speech_buffer.append(audio_data.copy())
            
            # Check for silence
            rms = float(np.sqrt(np.mean(audio_data ** 2)))
            
            if rms < self.silence_threshold:
                self.silence_duration += len(audio_data) / 16000.0  # assuming 16kHz
            else:
                self.silence_duration = 0.0
            
            # If enough silence, process speech
            if self.silence_duration >= self.speech_timeout:
                logger.info("Speech capture complete (silence detected)")
                self._process_speech()

    def _process_speech(self) -> None:
        """Process captured speech through STT."""
        if not self.speech_buffer:
            logger.warning("No speech to process")
            self.capturing_speech = False
            self._set_state(PipelineState.LISTENING)
            return
        
        # Concatenate speech buffer
        speech_audio = np.concatenate(self.speech_buffer)
        self.speech_buffer.clear()
        self.capturing_speech = False
        
        logger.info(f"Processing {len(speech_audio)} samples...")
        
        # Run STT in separate thread to not block audio
        threading.Thread(
            target=self._run_stt,
            args=(speech_audio,),
            daemon=True
        ).start()

    def _run_stt(self, audio_data: np.ndarray) -> None:
        """
        Run STT on audio data.
        
        Args:
            audio_data: Audio samples
        """
        try:
            if self.stt_mode == "offline":
                # Offline STT
                if not self.stt_offline:
                    logger.error("Offline STT not initialized")
                    return
                
                transcript = self.stt_offline.transcribe(audio_data, sample_rate=16000)
            else:
                # Cloud STT (synchronous wrapper for now)
                if not self.stt_cloud:
                    logger.error("Cloud STT not initialized")
                    return
                
                # For Realtime API, we'd use streaming
                # This is a simplified version
                transcript = "Cloud STT not fully implemented yet"
            
            if transcript:
                logger.info(f"Transcript: {transcript}")
                
                # Call user callback
                if self.on_transcript:
                    try:
                        self.on_transcript(transcript)
                    except Exception as e:
                        logger.error(f"Error in transcript callback: {e}")
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            self._set_state(PipelineState.ERROR)
        finally:
            self._set_state(PipelineState.LISTENING)

    def start(self) -> None:
        """Start the audio pipeline."""
        if self.running:
            logger.warning("Pipeline already running")
            return
        
        logger.info("Starting audio pipeline...")
        
        try:
            # Initialize wake word detector
            access_key = self.wake_word_config.get("access_key")
            if access_key:
                keywords = [self.wake_word_config.get("keyword", "jarvis")]
                sensitivity = self.wake_word_config.get("sensitivity", 0.5)
                
                self.wake_word_detector = WakeWordDetector(
                    access_key=access_key,
                    keywords=keywords,
                    sensitivities=[sensitivity],
                    callback=self._on_wake_word_detected
                )
                logger.info("Wake word detector initialized")
            else:
                logger.warning("No wake word access key provided")
            
            # Initialize STT
            if self.stt_mode == "offline":
                model_path = self.stt_config.get("model_path", "models/ggml-base.en.bin")
                whisper_bin = self.stt_config.get("binary_path", "whisper-cpp/main")
                
                self.stt_offline = WhisperSTT(
                    model_path=model_path,
                    whisper_bin=whisper_bin
                )
                logger.info("Offline STT initialized")
            else:
                api_key = self.stt_config.get("api_key")
                if api_key:
                    self.stt_cloud = RealtimeSTT(
                        api_key=api_key,
                        on_transcript=self.on_transcript
                    )
                    logger.info("Cloud STT initialized")
                else:
                    logger.warning("No OpenAI API key provided")
            
            # Initialize audio capture
            self.audio_capture = AudioCapture(
                sample_rate=16000,
                channels=1,
                chunk_duration_ms=30,
                callback=self._on_audio_frame
            )
            
            # Start capturing
            self.audio_capture.start()
            self.running = True
            
            self._set_state(PipelineState.LISTENING)
            logger.info("Audio pipeline started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            self._set_state(PipelineState.ERROR)
            raise

    def stop(self) -> None:
        """Stop the audio pipeline."""
        if not self.running:
            return
        
        logger.info("Stopping audio pipeline...")
        
        self.running = False
        self.capturing_speech = False
        
        # Stop audio capture
        if self.audio_capture:
            self.audio_capture.stop()
        
        # Cleanup wake word detector
        if self.wake_word_detector:
            self.wake_word_detector.delete()
        
        self._set_state(PipelineState.STOPPED)
        logger.info("Audio pipeline stopped")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()





