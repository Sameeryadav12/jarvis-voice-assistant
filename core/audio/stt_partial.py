"""
Partial Result Captions - Real-time Transcription Streaming

Streams partial transcription results from STT backends and updates UI in real-time.
"""

import sys
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from threading import Thread, Event
import numpy as np
from loguru import logger
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.audio.stt_faster_whisper import FasterWhisperSTT


@dataclass
class PartialResult:
    """Represents a partial transcription result."""
    
    text: str
    is_final: bool
    timestamp: float
    confidence: float = 0.0
    language: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "is_final": self.is_final,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "language": self.language,
        }


class PartialResultStreamer:
    """
    Streams partial transcription results from STT backends.
    
    Features:
    - Real-time partial results
    - Final result commitment
    - UI update callbacks
    - Cancellation support
    """
    
    def __init__(
        self,
        stt_backend,
        chunk_duration_ms: int = 500,
        min_chunk_duration_ms: int = 250,
    ):
        """
        Initialize partial result streamer.
        
        Args:
            stt_backend: STT backend instance (must support streaming)
            chunk_duration_ms: Duration of audio chunks to process (ms)
            min_chunk_duration_ms: Minimum chunk duration before processing (ms)
        """
        self.stt_backend = stt_backend
        self.chunk_duration_ms = chunk_duration_ms
        self.min_chunk_duration_ms = min_chunk_duration_ms
        self.sample_rate = 16000  # Standard for speech
        
        # State
        self.is_streaming = False
        self.audio_buffer: List[np.ndarray] = []
        self.current_result: Optional[PartialResult] = None
        self.final_results: List[PartialResult] = []
        
        # Threading
        self.processing_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Callbacks
        self.on_partial_result: Optional[Callable[[PartialResult], None]] = None
        self.on_final_result: Optional[Callable[[PartialResult], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
    
    def set_callbacks(
        self,
        on_partial_result: Optional[Callable[[PartialResult], None]] = None,
        on_final_result: Optional[Callable[[PartialResult], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Set callbacks for results.
        
        Args:
            on_partial_result: Called with each partial result
            on_final_result: Called when result is finalized
            on_error: Called on errors
        """
        self.on_partial_result = on_partial_result
        self.on_final_result = on_final_result
        self.on_error = on_error
    
    def add_audio_chunk(self, audio_chunk: np.ndarray):
        """
        Add audio chunk for processing.
        
        Args:
            audio_chunk: Audio samples (numpy array)
        """
        if not self.is_streaming:
            return
        
        self.audio_buffer.append(audio_chunk)
        
        # Trigger processing if buffer is large enough
        total_samples = sum(len(chunk) for chunk in self.audio_buffer)
        total_duration_ms = (total_samples / self.sample_rate) * 1000
        
        if total_duration_ms >= self.min_chunk_duration_ms:
            self._process_buffer()
    
    def start_streaming(self):
        """Start streaming transcription."""
        if self.is_streaming:
            logger.warning("Already streaming")
            return
        
        logger.info("Starting partial result streaming")
        self.is_streaming = True
        self.audio_buffer.clear()
        self.current_result = None
        self.final_results.clear()
        self.stop_event.clear()
    
    def stop_streaming(self, finalize: bool = True) -> Optional[PartialResult]:
        """
        Stop streaming and optionally finalize result.
        
        Args:
            finalize: Whether to process remaining audio and return final result
            
        Returns:
            Final result if finalize=True, None otherwise
        """
        if not self.is_streaming:
            return None
        
        logger.info("Stopping partial result streaming")
        self.is_streaming = False
        self.stop_event.set()
        
        final_result = None
        
        if finalize and self.audio_buffer:
            # Process remaining audio
            final_result = self._process_final()
        
        # Wait for processing thread
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        return final_result
    
    def cancel(self):
        """Cancel streaming immediately."""
        logger.info("Canceling partial result streaming")
        self.is_streaming = False
        self.stop_event.set()
        self.audio_buffer.clear()
        self.current_result = None
    
    def _process_buffer(self):
        """Process audio buffer and generate partial result."""
        if not self.audio_buffer or self.stop_event.is_set():
            return
        
        # Combine chunks
        audio_data = np.concatenate(self.audio_buffer)
        
        # Spawn processing thread if not running
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = Thread(
                target=self._transcribe_chunk,
                args=(audio_data.copy(),),
                daemon=True,
            )
            self.processing_thread.start()
    
    def _transcribe_chunk(self, audio_data: np.ndarray):
        """Transcribe audio chunk in background thread."""
        try:
            # Transcribe using backend
            text = self.stt_backend.transcribe(
                audio_data,
                sample_rate=self.sample_rate,
            )
            
            if self.stop_event.is_set():
                return
            
            if text and text.strip():
                # Create partial result
                result = PartialResult(
                    text=text.strip(),
                    is_final=False,
                    timestamp=datetime.now().timestamp(),
                    confidence=0.0,  # STT backends may not provide confidence
                )
                
                self.current_result = result
                
                # Emit callback
                if self.on_partial_result:
                    try:
                        self.on_partial_result(result)
                    except Exception as e:
                        logger.error(f"Error in on_partial_result callback: {e}")
            
        except Exception as e:
            logger.error(f"Error transcribing chunk: {e}")
            if self.on_error:
                try:
                    self.on_error(e)
                except Exception as e2:
                    logger.error(f"Error in on_error callback: {e2}")
    
    def _process_final(self) -> Optional[PartialResult]:
        """Process remaining audio and return final result."""
        if not self.audio_buffer:
            return None
        
        try:
            # Combine all remaining chunks
            audio_data = np.concatenate(self.audio_buffer)
            
            # Transcribe
            text = self.stt_backend.transcribe(
                audio_data,
                sample_rate=self.sample_rate,
            )
            
            if text and text.strip():
                result = PartialResult(
                    text=text.strip(),
                    is_final=True,
                    timestamp=datetime.now().timestamp(),
                    confidence=0.0,
                )
                
                self.final_results.append(result)
                
                # Emit callback
                if self.on_final_result:
                    try:
                        self.on_final_result(result)
                    except Exception as e:
                        logger.error(f"Error in on_final_result callback: {e}")
                
                return result
            
        except Exception as e:
            logger.error(f"Error processing final result: {e}")
            if self.on_error:
                try:
                    self.on_error(e)
                except Exception as e2:
                    logger.error(f"Error in on_error callback: {e2}")
        
        return None


class FasterWhisperPartialStreamer(PartialResultStreamer):
    """
    Partial result streamer for faster-whisper backend.
    
    Uses faster-whisper's segment iteration for true streaming.
    """
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "int8",
        chunk_duration_ms: int = 500,
    ):
        """
        Initialize faster-whisper partial streamer.
        
        Args:
            model_size: Model size
            device: Device (cpu/cuda/auto)
            compute_type: Compute type
            chunk_duration_ms: Chunk duration
        """
        stt = FasterWhisperSTT(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
        )
        
        super().__init__(
            stt_backend=stt,
            chunk_duration_ms=chunk_duration_ms,
        )
    
    def _transcribe_chunk(self, audio_data: np.ndarray):
        """Transcribe using faster-whisper with segment iteration."""
        try:
            # Use faster-whisper's segment iteration for partial results
            segments, info = self.stt_backend.model.transcribe(
                audio_data,
                language=self.stt_backend.language,
                beam_size=self.stt_backend.beam_size,
                best_of=self.stt_backend.best_of,
            )
            
            if self.stop_event.is_set():
                return
            
            partial_text = ""
            
            # Collect segments as they come
            for segment in segments:
                if self.stop_event.is_set():
                    break
                
                partial_text += segment.text
                
                # Create partial result for each segment
                result = PartialResult(
                    text=partial_text.strip(),
                    is_final=False,
                    timestamp=datetime.now().timestamp(),
                    confidence=getattr(segment, 'avg_logprob', 0.0),
                )
                
                self.current_result = result
                
                # Emit callback
                if self.on_partial_result:
                    try:
                        self.on_partial_result(result)
                    except Exception as e:
                        logger.error(f"Error in on_partial_result callback: {e}")
            
            # Finalize if we got complete text
            if partial_text.strip() and not self.stop_event.is_set():
                final_result = PartialResult(
                    text=partial_text.strip(),
                    is_final=True,
                    timestamp=datetime.now().timestamp(),
                    confidence=getattr(info, 'language_probability', 0.0),
                    language=info.language if hasattr(info, 'language') else None,
                )
                
                self.final_results.append(final_result)
                
                if self.on_final_result:
                    try:
                        self.on_final_result(final_result)
                    except Exception as e:
                        logger.error(f"Error in on_final_result callback: {e}")
        
        except Exception as e:
            logger.error(f"Error transcribing with faster-whisper: {e}")
            if self.on_error:
                try:
                    self.on_error(e)
                except Exception as e2:
                    logger.error(f"Error in on_error callback: {e2}")


def create_partial_streamer(
    backend_type: str = "faster-whisper",
    **kwargs,
) -> PartialResultStreamer:
    """
    Create a partial result streamer for the specified backend.
    
    Args:
        backend_type: Backend type ("faster-whisper", etc.)
        **kwargs: Backend-specific arguments
        
    Returns:
        PartialResultStreamer instance
    """
    if backend_type == "faster-whisper":
        return FasterWhisperPartialStreamer(**kwargs)
    else:
        raise ValueError(f"Unsupported backend type: {backend_type}")

