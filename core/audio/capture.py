"""
Audio capture module using sounddevice.
Provides real-time microphone input with ring buffer implementation.
"""

import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from collections import deque
import threading
from loguru import logger


class RingBuffer:
    """
    Efficient ring buffer implementation for audio frames.
    Time complexity: O(1) for append and read operations.
    Space complexity: O(n) where n is max_size.
    """

    def __init__(self, max_size: int):
        """
        Initialize ring buffer.
        
        Args:
            max_size: Maximum number of elements to store
        """
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def append(self, data: np.ndarray) -> None:
        """
        Append audio data to buffer (O(1) operation).
        
        Args:
            data: Audio frame data
        """
        with self.lock:
            self.buffer.append(data.copy())

    def get_frames(self, num_frames: Optional[int] = None) -> list:
        """
        Get frames from buffer (O(k) where k is num_frames).
        
        Args:
            num_frames: Number of frames to retrieve, None for all
            
        Returns:
            List of audio frames
        """
        with self.lock:
            if num_frames is None:
                return list(self.buffer)
            else:
                return list(self.buffer)[-num_frames:]

    def clear(self) -> None:
        """Clear all frames from buffer (O(1) operation)."""
        with self.lock:
            self.buffer.clear()


class AudioCapture:
    """
    Real-time audio capture from microphone using sounddevice.
    Implements a ring buffer for efficient audio frame management.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration_ms: int = 30,
        buffer_size_seconds: int = 10,
        callback: Optional[Callable[[np.ndarray], None]] = None
    ):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz (16000 for speech)
            channels: Number of audio channels (1 for mono)
            chunk_duration_ms: Duration of each audio chunk in milliseconds
            buffer_size_seconds: Size of ring buffer in seconds
            callback: Optional callback function for real-time processing
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration_ms = chunk_duration_ms
        self.callback = callback
        
        # Calculate chunk size in samples
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        
        # Initialize ring buffer (stores ~10 seconds of audio by default)
        buffer_capacity = int(buffer_size_seconds * 1000 / chunk_duration_ms)
        self.ring_buffer = RingBuffer(max_size=buffer_capacity)
        
        # Stream state
        self.stream: Optional[sd.InputStream] = None
        self.is_recording = False
        
        logger.info(
            f"AudioCapture initialized: {sample_rate}Hz, "
            f"{channels}ch, {chunk_duration_ms}ms chunks"
        )

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status: sd.CallbackFlags
    ) -> None:
        """
        Internal callback for sounddevice stream.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Status flags
        """
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Store in ring buffer
        self.ring_buffer.append(indata)
        
        # Call user callback if provided
        if self.callback:
            try:
                self.callback(indata.copy())
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")

    def start(self) -> None:
        """Start audio capture stream."""
        if self.is_recording:
            logger.warning("Audio capture already running")
            return
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                blocksize=self.chunk_size,
                dtype=np.float32
            )
            self.stream.start()
            self.is_recording = True
            logger.info("Audio capture started")
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            raise

    def stop(self) -> None:
        """Stop audio capture stream."""
        if not self.is_recording:
            return
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        self.is_recording = False
        logger.info("Audio capture stopped")

    def get_audio_data(self, duration_seconds: Optional[float] = None) -> np.ndarray:
        """
        Get audio data from ring buffer.
        
        Args:
            duration_seconds: Duration of audio to retrieve, None for all
            
        Returns:
            Audio data as numpy array
        """
        if duration_seconds:
            num_frames = int(duration_seconds * 1000 / self.chunk_duration_ms)
            frames = self.ring_buffer.get_frames(num_frames)
        else:
            frames = self.ring_buffer.get_frames()
        
        if not frames:
            return np.array([], dtype=np.float32)
        
        return np.concatenate(frames)

    def clear_buffer(self) -> None:
        """Clear the audio ring buffer."""
        self.ring_buffer.clear()
        logger.debug("Audio buffer cleared")

    def get_rms_level(self, data: Optional[np.ndarray] = None) -> float:
        """
        Calculate RMS (Root Mean Square) audio level.
        Used for VU meter visualization.
        
        Args:
            data: Audio data, or None to use latest from buffer
            
        Returns:
            RMS level (0.0 to 1.0+)
        """
        if data is None:
            data = self.get_audio_data(duration_seconds=0.1)
        
        if len(data) == 0:
            return 0.0
        
        return float(np.sqrt(np.mean(data ** 2)))

    @staticmethod
    def list_devices() -> list:
        """
        List available audio devices.
        
        Returns:
            List of device information dictionaries
        """
        return sd.query_devices()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def create_vu_meter(level: float, width: int = 50) -> str:
    """
    Create a simple VU meter visualization.
    
    Args:
        level: Audio level (0.0 to 1.0)
        width: Width of the meter in characters
        
    Returns:
        String representation of the meter
    """
    level = min(max(level, 0.0), 1.0)  # Clamp to 0-1
    filled = int(level * width)
    bar = "#" * filled + "-" * (width - filled)
    return f"|{bar}| {level*100:.1f}%"

