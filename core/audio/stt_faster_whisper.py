"""
Fast Speech-to-Text using faster-whisper.

faster-whisper is a reimplementation of Whisper with CTranslate2,
providing 2-4× speedups with quantization support.
"""

import sys
from typing import Optional, Tuple
import numpy as np
from loguru import logger

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning(
        "faster-whisper not available. Install: pip install faster-whisper"
    )


class FasterWhisperSTT:
    """
    Fast local STT using faster-whisper.
    
    Features:
    - 2-4× faster than standard Whisper
    - 8-bit quantization support
    - Auto device selection (CPU/GPU)
    - Multiple model sizes (tiny/base/small/medium/large)
    """
    
    # Available models and their specs
    MODELS = {
        "tiny": {"size": "39M", "speed": "very fast", "accuracy": "good"},
        "base": {"size": "74M", "speed": "fast", "accuracy": "better"},
        "small": {"size": "244M", "speed": "medium", "accuracy": "best"},
        "medium": {"size": "769M", "speed": "slow", "accuracy": "excellent"},
        "large": {"size": "1550M", "speed": "very slow", "accuracy": "best"},
    }
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "int8",
        language: Optional[str] = "en",
        beam_size: int = 5,
        best_of: int = 5,
        vad_filter: bool = True,
    ):
        """
        Initialize Faster Whisper STT.
        
        Args:
            model_size: Model size ("tiny", "base", "small", "medium", "large")
            device: Device ("cpu", "cuda", or convert "auto")
            compute_type: Compute type ("int8", "int8_float16", "float16", "float32")
            language: Language code (or None for auto-detect)
            beam_size: Beam search width
            best_of: Number of candidates to consider
            vad_filter: Use internal VAD filtering
        """
        if not FASTER_WHISPER_AVAILABLE:
            raise ImportError(
                "faster-whisper not available. "
                "Install: pip install faster-whisper"
            )
        
        if model_size not in self.MODELS:
            raise ValueError(
                f"Invalid model_size: {model_size}. "
                f"Choose from: {list(self.MODELS.keys())}"
            )
        
        self.model_size = model_size
        self.language = language
        self.beam_size = beam_size
        self.best_of = best_of
        self.vad_filter = vad_filter
        
        # Auto-select device
        if device == "auto":
            device = self._auto_select_device()
        
        self.device = device
        self.compute_type = compute_type
        
        # Load model
        logger.info(
            f"Loading faster-whisper model: {model_size} "
            f"(device: {device}, compute: {compute_type})"
        )
        
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=1,
            )
            logger.info("faster-whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            raise
    
    def _auto_select_device(self) -> str:
        """Auto-select best device (CPU or CUDA)."""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info("CUDA available, using GPU")
                return "cuda"
            else:
                logger.info("CUDA not available, using CPU")
                return "cpu"
        except ImportError:
            return "cpu"
    
    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio samples as numpy array (16kHz, float32)
            sample_rate: Sample rate (should be 16000)
            language: Language code (or None to auto-detect)
            
        Returns:
            Transcribed text
        """
        if audio_data is None or len(audio_data) == 0:
            return ""
        
        try:
            # Use provided language or fall back to instance language
            transcribe_language = language or self.language
            
            # Run transcription
            segments, info = self.model.transcribe(
                audio_data,
                language=transcribe_language,
                beam_size=self.beam_size,
                best_of=self.best_of,
                vad_filter=self.vad_filter,
            )
            
            # Combine segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            
            transcript = " ".join(text_parts).strip()
            
            # Log info for debugging
            logger.debug(
                f"Transcribed: '{transcript[:50]}...' "
                f"(language={info.language}, "
                f"probability={info.language_probability:.2f})"
            )
            
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    def transcribe_stream(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000,
    ) -> Optional[str]:
        """
        Transcribe a single audio chunk (streaming mode).
        
        Note: faster-whisper doesn't support true streaming,
        but this can be used for real-time-style processing.
        
        Args:
            audio_chunk: Audio chunk as numpy array
            sample_rate: Sample rate
            
        Returns:
            Transcribed text or None if too short
        """
        # Minimum duration for transcription (100ms)
        min_duration = 0.1
        min_samples = int(sample_rate * min_duration)
        
        if len(audio_chunk) < min_samples:
            return None
        
        return self.transcribe(audio_chunk, sample_rate)
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "language": self.language,
            **self.MODELS.get(self.model_size, {}),
        }
    
    @classmethod
    def list_models(cls) -> dict:
        """List available models and their specs."""
        return cls.MODELS
    
    def is_available(self) -> bool:
        """Check if faster-whisper is available."""
        return FASTER_WHISPER_AVAILABLE


def create_faster_whisper(
    model_size: str = "base",
    device: str = "auto",
    compute_type: str = "int8",
    **kwargs
) -> Optional[FasterWhisperSTT]:
    """
    Factory function to create Faster Whisper STT instance.
    
    Args:
        model_size: Model size ("tiny", "base", "small", etc.)
        device: Device ("cpu", "cuda", or "auto")
        compute_type: Compute type ("int8", "float16", etc.)
        **kwargs: Additional STT parameters
        
    Returns:
        FasterWhisperSTT instance or None if not available
    """
    if not FASTER_WHISPER_AVAILABLE:
        logger.warning(
            "faster-whisper not available, cannot create STT backend"
        )
        return None
    
    try:
        return FasterWhisperSTT(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to initialize faster-whisper: {e}")
        return None


# Test function
if __name__ == "__main__":
    import sounddevice as sd
    import time
    
    logger.info("Testing faster-whisper STT...")
    
    try:
        # Create STT
        stt = create_faster_whisper(model_size="tiny")
        
        if stt:
            print("Available models:")
            for name, specs in FasterWhisperSTT.list_models().items():
                print(f"  {name}: {specs}")
            
            print(f"\nUsing model: {stt.get_model_info()}")
            print("\nRecording 5 seconds of audio...")
            
            # Record audio
            sample_rate = 16000
            duration = 5
            audio_data = sd.rec(
                int(sample_rate * duration),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            print("Transcribing...")
            start_time = time.time()
            transcript = stt.transcribe(audio_data[:, 0], sample_rate)
            elapsed = time.time() - start_time
            
            print(f"Transcribed in {elapsed:.2f}s:")
            print(f"'{transcript}'")
        else:
            print("STT not available")
    
    except KeyboardInterrupt:
        print("\nStopped")

