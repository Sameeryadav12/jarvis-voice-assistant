"""
Voice Activity Detection (VAD) using Silero VAD

Detects when speech starts and stops to gate audio frames.
Only sends voiced frames to STT for lower latency and CPU usage.
"""

import sys
from typing import Optional, Callable
import numpy as np
from loguru import logger

try:
    import torch
    SILERO_AVAILABLE = True
except ImportError:
    SILERO_AVAILABLE = False
    logger.warning("Silero VAD not available. Install: pip install silero-vad torch")


class SileroVAD:
    """
    Silero VAD implementation for speech start/stop detection.
    
    Features:
    - Real-time VAD on audio stream
    - Configurable thresholds for start/stop detection
    - Automatic model loading
    """
    
    def __init__(
        self,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        max_speech_duration_s: float = float('inf'),
        min_silence_duration_ms: int = 500,
        speech_pad_ms: int = 400,
        sample_rate: int = 16000,
    ):
        """
        Initialize Silero VAD.
        
        Args:
            threshold: Detection threshold (0.0-1.0). Higher = more strict
            min_speech_duration_ms: Minimum speech duration to trigger "start"
            max_speech_duration_s: Maximum speech duration before forcing stop
            min_silence_duration_ms: Minimum silence to trigger "stop"
            speech_pad_ms: Extra padding around speech segments
            sample_rate: Audio sample rate (Hz)
        """
        if not SILERO_AVAILABLE:
            raise ImportError(
                "Silero VAD not available. Install: pip install silero-vad"
            )
        
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_speech_duration_s = max_speech_duration_s
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        self.sample_rate = sample_rate
        
        # Load model using correct API
        logger.info("Loading Silero VAD model...")
        
        # Load Silero VAD model from torch hub
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=True,
            trust_repo=True
        )
        
        # Only call eval() if it's not ONNX wrapper
        if hasattr(self.model, 'eval'):
            self.model.eval()
        
        self.get_speech_timestamps = utils[0]
        
        logger.info("Silero VAD model loaded successfully")
        
        # State tracking
        self.is_speaking = False
        self.speech_start_frame = None
        self.last_voice_frame = None
        self.silence_frames = 0
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_stop: Optional[Callable] = None
    
    def set_callbacks(
        self,
        on_speech_start: Optional[Callable] = None,
        on_speech_stop: Optional[Callable] = None,
    ):
        """
        Set callbacks for speech start/stop events.
        
        Args:
            on_speech_start: Called when speech starts
            on_speech_stop: Called when speech stops
        """
        self.on_speech_start = on_speech_start
        self.on_speech_stop = on_speech_stop
    
    def process_chunk(self, audio_chunk: np.ndarray) -> tuple[bool, float]:
        """
        Process audio chunk and detect speech.
        
        Args:
            audio_chunk: Audio samples as numpy array (16kHz, float32)
            
        Returns:
            tuple: (is_speaking, probability)
                - is_speaking: Whether speech is currently detected
                - probability: Speech probability (0.0-1.0)
        """
        if audio_chunk is None or len(audio_chunk) == 0:
            return False, 0.0
        
        # Silero VAD requires exactly 512 samples at 16kHz
        # Pad or truncate to 512 samples
        if len(audio_chunk) < 512:
            # Pad with zeros
            padded = np.pad(audio_chunk, (0, 512 - len(audio_chunk)), 'constant')
        elif len(audio_chunk) > 512:
            # Take first 512 samples
            padded = audio_chunk[:512]
        else:
            padded = audio_chunk
        
        # Convert to torch tensor (add batch dimension)
        audio_tensor = torch.from_numpy(padded).unsqueeze(0)
        
        # Get speech probability
        with torch.no_grad():
            speech_prob = self.model(audio_tensor, self.sample_rate).item()
        
        # Detect speech based on threshold
        currently_speaking = speech_prob > self.threshold
        
        # Update state
        now_frames = int(len(audio_chunk) / self.sample_rate * 1000)
        
        if currently_speaking:
            self.silence_frames = 0
            
            if not self.is_speaking:
                # Speech start
                self.is_speaking = True
                self.speech_start_frame = now_frames
                logger.debug(f"Speech detected (probability: {speech_prob:.2f})")
                
                if self.on_speech_start:
                    self.on_speech_start()
            
            self.last_voice_frame = now_frames
        else:
            self.silence_frames += now_frames
            
            if self.is_speaking:
                # Check if should stop
                should_stop = (
                    self.silence_frames >= self.min_silence_duration_ms or
                    (self.last_voice_frame and 
                     (now_frames - self.last_voice_frame) >= 
                     self.max_speech_duration_s * 1000)
                )
                
                if should_stop:
                    # Speech stop
                    self.is_speaking = False
                    speech_duration_ms = (
                        (now_frames - self.speech_start_frame) 
                        if self.speech_start_frame else 0
                    )
                    logger.debug(
                        f"Speech ended "
                        f"(duration: {speech_duration_ms}ms, "
                        f"final_prob: {speech_prob:.2f})"
                    )
                    
                    if self.on_speech_stop:
                        self.on_speech_stop()
        
        return self.is_speaking, speech_prob
    
    def reset(self):
        """Reset VAD state."""
        self.is_speaking = False
        self.speech_start_frame = None
        self.last_voice_frame = None
        self.silence_frames = 0
    
    def is_available(self) -> bool:
        """Check if Silero VAD is available."""
        return SILERO_AVAILABLE


def create_vad(
    threshold: float = 0.5,
    min_speech_duration_ms: int = 250,
    min_silence_duration_ms: int = 500,
    **kwargs
) -> Optional[SileroVAD]:
    """
    Factory function to create VAD instance.
    
    Args:
        threshold: Detection threshold
        min_speech_duration_ms: Minimum speech duration
        min_silence_duration_ms: Minimum silence duration
        **kwargs: Additional VAD parameters
        
    Returns:
        SileroVAD instance or None if not available
    """
    if not SILERO_AVAILABLE:
        logger.warning("Silero VAD not available, VAD will be disabled")
        return None
    
    try:
        return SileroVAD(
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to initialize Silero VAD: {e}")
        return None


# Test function
if __name__ == "__main__":
    import sounddevice as sd
    import time
    
    logger.info("Testing Silero VAD...")
    
    try:
        vad = create_vad(threshold=0.5)
        
        if vad:
            print("Speak now... (Ctrl+C to stop)")
            
            def on_start():
                print("[VAD] Speech started")
            
            def on_stop():
                print("[VAD] Speech stopped")
            
            vad.set_callbacks(on_speech_start=on_start, on_speech_stop=on_stop)
            
            # Record audio in chunks (Silero VAD needs at least 512 samples)
            sample_rate = 16000
            chunk_duration_ms = 100  # At least 32ms at 16kHz (512 samples)
            chunk_size = int(sample_rate * chunk_duration_ms / 1000)
            
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype='float32',
                blocksize=chunk_size
            ):
                while True:
                    audio_chunk = sd.rec(chunk_size, samplerate=sample_rate, channels=1)[:, 0]
                    vad.process_chunk(audio_chunk)
                    time.sleep(chunk_duration_ms / 1000)
        
        else:
            print("VAD not available")
    
    except KeyboardInterrupt:
        print("\nStopped")

