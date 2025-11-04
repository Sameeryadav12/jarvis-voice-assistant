"""
Audio Ring Buffer with VAD Gating

Implements a circular buffer that only accumulates audio when VAD detects speech.
This reduces latency and CPU usage by skipping silence.
"""

import sys
from typing import Optional, Callable, List
import numpy as np
from collections import deque
from loguru import logger


class AudioRingBuffer:
    """
    Ring buffer for audio data with VAD gating.
    
    Features:
    - Circular buffer for continuous audio streaming
    - VAD-based gating (only add when speech detected)
    - Configurable buffer size and threshold
    - Automatic overflow handling
    - Speech start/stop detection
    """
    
    def __init__(
        self,
        buffer_duration_ms: int = 3000,
        sample_rate: int = 16000,
        vad_threshold: float = 0.5,
        chunk_duration_ms: int = 30,
    ):
        """
        Initialize audio ring buffer.
        
        Args:
            buffer_duration_ms: Total buffer duration in milliseconds
            sample_rate: Audio sample rate in Hz
            vad_threshold: VAD probability threshold
            chunk_duration_ms: Duration of each audio chunk in milliseconds
        """
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.vad_threshold = vad_threshold
        
        # Calculate buffer size in samples
        self.buffer_size_samples = int(
            sample_rate * (buffer_duration_ms / 1000)
        )
        self.chunk_size_samples = int(
            sample_rate * (chunk_duration_ms / 1000)
        )
        
        # Circular buffer
        self.buffer = deque(maxlen=self.buffer_size_samples)
        
        # VAD state
        self.is_recording = False
        self.speech_detected = False
        
        # Statistics
        self.total_samples_added = 0
        self.total_samples_skipped = 0
        
        logger.debug(
            f"AudioRingBuffer initialized: "
            f"size={buffer_duration_ms}ms, "
            f"chunk={chunk_duration_ms}ms, "
            f"vad_threshold={vad_threshold}"
        )
    
    def add_chunk(
        self,
        audio_chunk: np.ndarray,
        speech_probability: float = 1.0,
    ) -> bool:
        """
        Add audio chunk to buffer (with optional VAD gating).
        
        Args:
            audio_chunk: Audio samples as numpy array
            speech_probability: Probability that audio contains speech (0.0-1.0)
            
        Returns:
            True if chunk was added, False if skipped
        """
        # Check if should add based on VAD
        should_add = (
            self.is_recording or  # Force record mode
            speech_probability > self.vad_threshold  # VAD detected speech
        )
        
        if should_add:
            # Add to buffer
            for sample in audio_chunk:
                self.buffer.append(float(sample))
            
            self.total_samples_added += len(audio_chunk)
            
            # Update speech state
            if speech_probability > self.vad_threshold:
                if not self.speech_detected:
                    logger.debug("Speech detected in audio buffer")
                    self.speech_detected = True
            else:
                if self.speech_detected:
                    logger.debug("Speech ended in audio buffer")
                    self.speech_detected = False
            
            return True
        else:
            # Skip silence
            self.total_samples_skipped += len(audio_chunk)
            return False
    
    def get_buffer(self) -> np.ndarray:
        """
        Get current buffer contents as numpy array.
        
        Returns:
            Audio samples as numpy array
        """
        return np.array(self.buffer, dtype=np.float32)
    
    def get_buffer_duration(self) -> float:
        """
        Get current buffer duration in seconds.
        
        Returns:
            Duration in seconds
        """
        return len(self.buffer) / self.sample_rate
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) >= self.buffer_size_samples
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0
    
    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()
        self.speech_detected = False
        logger.debug("Audio buffer cleared")
    
    def set_recording(self, enabled: bool):
        """
        Set forced recording mode (ignore VAD).
        
        Args:
            enabled: If True, record all audio regardless of VAD
        """
        if enabled != self.is_recording:
            logger.debug(f"Forced recording mode: {enabled}")
            self.is_recording = enabled
            
            if not enabled:
                # Reset speech state when stopping forced recording
                self.speech_detected = False
    
    def get_statistics(self) -> dict:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_samples = self.total_samples_added + self.total_samples_skipped
        skip_ratio = (
            self.total_samples_skipped / total_samples 
            if total_samples > 0 else 0.0
        )
        
        return {
            "buffer_size": len(self.buffer),
            "buffer_duration_ms": self.get_buffer_duration() * 1000,
            "is_full": self.is_full(),
            "is_recording": self.is_recording,
            "speech_detected": self.speech_detected,
            "samples_added": self.total_samples_added,
            "samples_skipped": self.total_samples_skipped,
            "skip_ratio": skip_ratio,
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.total_samples_added = 0
        self.total_samples_skipped = 0


class VadGatedAudioBuffer:
    """
    Combined VAD + Audio Buffer for efficient speech detection and recording.
    
    This class integrates VAD with audio buffering to only record when speech
    is detected, significantly reducing CPU usage and improving responsiveness.
    """
    
    def __init__(
        self,
        vad,
        buffer_duration_ms: int = 3000,
        sample_rate: int = 16000,
        pre_speech_buffer_ms: int = 200,
        post_speech_buffer_ms: int = 500,
    ):
        """
        Initialize VAD-gated audio buffer.
        
        Args:
            vad: VAD instance (SileroVAD or compatible)
            buffer_duration_ms: Total buffer duration in milliseconds
            sample_rate: Audio sample rate in Hz
            pre_speech_buffer_ms: Audio to keep before speech starts
            post_speech_buffer_ms: Audio to keep after speech ends
        """
        self.vad = vad
        self.sample_rate = sample_rate
        self.pre_speech_buffer_ms = pre_speech_buffer_ms
        self.post_speech_buffer_ms = post_speech_buffer_ms
        
        # Create ring buffer
        self.buffer = AudioRingBuffer(
            buffer_duration_ms=buffer_duration_ms,
            sample_rate=sample_rate,
        )
        
        # State tracking
        self.speech_buffer_samples = int(
            sample_rate * (pre_speech_buffer_ms / 1000)
        )
        self.pre_speech_samples = deque(maxlen=self.speech_buffer_samples)
        
        self.waiting_for_speech_end = False
        self.speech_end_samples = int(
            sample_rate * (post_speech_buffer_ms / 1000)
        )
        self.silence_samples_count = 0
        
        # Callbacks
        self.on_speech_complete: Optional[Callable[[np.ndarray], None]] = None
        
        logger.info(
            f"VadGatedAudioBuffer initialized: "
            f"pre_buffer={pre_speech_buffer_ms}ms, "
            f"post_buffer={post_speech_buffer_ms}ms"
        )
    
    def process_chunk(self, audio_chunk: np.ndarray):
        """
        Process audio chunk with VAD gating.
        
        Args:
            audio_chunk: Audio samples as numpy array
        """
        # Run VAD
        is_speaking, speech_prob = self.vad.process_chunk(audio_chunk)
        
        if is_speaking:
            # Speech detected - add to pre-speech buffer and main buffer
            for sample in audio_chunk:
                self.pre_speech_samples.append(sample)
                self.buffer.buffer.append(sample)
            
            self.waiting_for_speech_end = False
            self.silence_samples_count = 0
        else:
            # Silence
            if self.waiting_for_speech_end:
                # We're waiting for post-speech buffer to fill
                self.silence_samples_count += len(audio_chunk)
                
                if self.silence_samples_count >= self.speech_end_samples:
                    # Enough silence - speech is complete
                    self._trigger_speech_complete()
                    self.silence_samples_count = 0
                    self.waiting_for_speech_end = False
            else:
                # Add to pre-speech buffer (save for later)
                for sample in audio_chunk:
                    self.pre_speech_samples.append(sample)
    
    def _trigger_speech_complete(self):
        """Trigger speech complete callback with buffered audio."""
        if self.on_speech_complete:
            # Get complete audio (pre-speech + buffer)
            complete_audio = np.concatenate([
                np.array(self.pre_speech_samples, dtype=np.float32),
                self.buffer.get_buffer()
            ])
            
            # Trigger callback
            self.on_speech_complete(complete_audio)
            
            # Clear buffers
            self.buffer.clear()
            self.pre_speech_samples.clear()
    
    def set_speech_complete_callback(self, callback: Callable[[np.ndarray], None]):
        """
        Set callback for when speech is complete.
        
        Args:
            callback: Function to call with complete audio array
        """
        self.on_speech_complete = callback
    
    def get_statistics(self) -> dict:
        """Get combined statistics."""
        buffer_stats = self.buffer.get_statistics()
        vad_stats = {
            "pre_speech_buffer_samples": len(self.pre_speech_samples),
            "waiting_for_speech_end": self.waiting_for_speech_end,
            "silence_samples_count": self.silence_samples_count,
        }
        return {**buffer_stats, **vad_stats}


# Test function
if __name__ == "__main__":
    import sounddevice as sd
    import time
    
    logger.info("Testing VAD-Gated Audio Buffer...")
    
    try:
        from vad import create_vad
        
        # Create VAD and buffer
        vad = create_vad(threshold=0.5)
        buffer = VadGatedAudioBuffer(
            vad=vad,
            buffer_duration_ms=3000,
            pre_speech_buffer_ms=200,
            post_speech_buffer_ms=500,
        )
        
        # Set callback
        def on_speech(audio):
            duration = len(audio) / 16000
            print(f"[Callback] Speech received: {duration:.2f}s, {len(audio)} samples")
        
        buffer.set_speech_complete_callback(on_speech)
        
        print("Recording with VAD gating... (speak and then wait)")
        
        # Record audio
        sample_rate = 16000
        chunk_duration_ms = 30
        chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            blocksize=chunk_size
        ) as stream:
            start_time = time.time()
            while time.time() - start_time < 60:  # 60s timeout
                audio_chunk = stream.read(chunk_size)[0][:, 0]
                buffer.process_chunk(audio_chunk)
                time.sleep(chunk_duration_ms / 1000)
        
        # Print statistics
        stats = buffer.get_statistics()
        print("\nBuffer statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        logger.error(f"Test failed: {e}")

