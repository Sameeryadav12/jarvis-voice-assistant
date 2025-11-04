"""
Secure Microphone Input Handler
Uses pyaudio for audio capture with proper resource management
"""

import pyaudio
import numpy as np
import wave
import threading
import logging
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int = 16000  # 16kHz for speech
    channels: int = 1  # Mono
    chunk_size: int = 512  # Small chunks for low latency
    format: int = pyaudio.paInt16  # 16-bit audio


class SecureMicrophone:
    """
    Secure microphone handler with proper resource management.
    All processing happens locally - no cloud uploads without consent.
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.is_recording = False
        self.audio_buffer = []
        self.lock = threading.Lock()
        
        logger.info(f"Initialized SecureMicrophone: {self.config.sample_rate}Hz, {self.config.channels}ch")
    
    def list_devices(self):
        """List available audio input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        return devices
    
    def start_recording(self, callback: Optional[Callable] = None):
        """
        Start recording audio from microphone.
        
        Args:
            callback: Optional callback for real-time audio chunks (chunk_data, is_speaking)
        """
        if self.is_recording:
            logger.warning("Already recording")
            return False
        
        try:
            self.stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size,
                stream_callback=None  # Use blocking mode for simplicity
            )
            
            self.is_recording = True
            self.audio_buffer = []
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._record_loop,
                args=(callback,),
                daemon=True
            )
            self.recording_thread.start()
            
            logger.info("Started recording")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def _record_loop(self, callback: Optional[Callable]):
        """Internal recording loop."""
        while self.is_recording and self.stream:
            try:
                # Read audio chunk
                data = self.stream.read(self.config.chunk_size, exception_on_overflow=False)
                
                # Store in buffer
                with self.lock:
                    self.audio_buffer.append(data)
                
                # Call callback if provided
                if callback:
                    callback(data)
                    
            except Exception as e:
                logger.error(f"Error in recording loop: {e}")
                break
    
    def stop_recording(self) -> bytes:
        """
        Stop recording and return recorded audio data.
        
        Returns:
            Raw audio data as bytes
        """
        if not self.is_recording:
            logger.warning("Not recording")
            return b""
        
        self.is_recording = False
        
        # Wait for thread to finish
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=1.0)
        
        # Stop stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Get buffered audio
        with self.lock:
            audio_data = b"".join(self.audio_buffer)
            self.audio_buffer = []
        
        logger.info(f"Stopped recording: {len(audio_data)} bytes")
        return audio_data
    
    def save_to_wav(self, audio_data: bytes, output_path: Path):
        """Save audio data to WAV file."""
        try:
            with wave.open(str(output_path), 'wb') as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.config.format))
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(audio_data)
            
            logger.info(f"Saved audio to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False
    
    def get_audio_level(self, audio_data: bytes) -> float:
        """
        Get audio level (RMS) from raw audio data.
        Returns value between 0.0 and 1.0
        """
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate RMS
            rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
            
            # Normalize to 0-1 range (assuming max int16 value)
            normalized = min(rms / 10000.0, 1.0)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to calculate audio level: {e}")
            return 0.0
    
    def cleanup(self):
        """Clean up resources."""
        if self.is_recording:
            self.stop_recording()
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        logger.info("Cleaned up SecureMicrophone")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class AudioLevelMonitor:
    """Monitor audio levels in real-time."""
    
    def __init__(self, microphone: SecureMicrophone):
        self.microphone = microphone
        self.current_level = 0.0
        self.lock = threading.Lock()
    
    def update_level(self, audio_chunk: bytes):
        """Update current audio level."""
        level = self.microphone.get_audio_level(audio_chunk)
        with self.lock:
            self.current_level = level
    
    def get_level(self) -> float:
        """Get current audio level."""
        with self.lock:
            return self.current_level

