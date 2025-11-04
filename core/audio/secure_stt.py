"""
Secure Speech-to-Text Handler
Uses faster-whisper for LOCAL processing - no cloud uploads
"""

import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class STTResult:
    """STT result."""
    text: str
    language: str
    confidence: float
    success: bool


class SecureSTT:
    """
    Secure STT using faster-whisper.
    All processing happens locally - your voice never leaves your computer.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize STT with specified model size.
        
        Args:
            model_size: Model size - tiny, base, small, medium, large
                       Smaller = faster, larger = more accurate
        """
        self.model_size = model_size
        self.model = None
        self.initialized = False
        
        logger.info(f"Initializing SecureSTT with model: {model_size}")
    
    def initialize(self) -> bool:
        """Initialize the STT model (lazy loading)."""
        if self.initialized:
            return True
        
        try:
            from faster_whisper import WhisperModel
            
            # Load model (downloads on first run, then cached locally)
            logger.info(f"Loading faster-whisper model '{self.model_size}'...")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # Use CPU for compatibility
                compute_type="int8"  # Optimized for speed
            )
            
            self.initialized = True
            logger.info("STT model loaded successfully")
            return True
            
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
            return False
    
    def transcribe_file(self, audio_path: Path) -> STTResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
        
        Returns:
            STTResult with transcription
        """
        if not self.initialized:
            if not self.initialize():
                return STTResult(
                    text="",
                    language="",
                    confidence=0.0,
                    success=False
                )
        
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            # Transcribe (happens locally on your computer)
            segments, info = self.model.transcribe(
                str(audio_path),
                beam_size=5,
                language="en",  # Set to English for better accuracy
                condition_on_previous_text=False
            )
            
            # Collect all segments
            text_parts = []
            avg_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                text_parts.append(segment.text.strip())
                avg_confidence += segment.avg_logprob
                segment_count += 1
            
            # Combine text
            full_text = " ".join(text_parts).strip()
            
            # Calculate average confidence
            if segment_count > 0:
                avg_confidence = avg_confidence / segment_count
                # Convert log probability to 0-1 scale (approximate)
                confidence = min(max((avg_confidence + 1.0) / 1.0, 0.0), 1.0)
            else:
                confidence = 0.0
            
            logger.info(f"Transcription complete: '{full_text}' (confidence: {confidence:.2f})")
            
            return STTResult(
                text=full_text,
                language=info.language,
                confidence=confidence,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return STTResult(
                text="",
                language="",
                confidence=0.0,
                success=False
            )
    
    def transcribe_bytes(self, audio_data: bytes, sample_rate: int = 16000) -> STTResult:
        """
        Transcribe raw audio bytes to text.
        
        Args:
            audio_data: Raw audio data (PCM 16-bit)
            sample_rate: Sample rate in Hz
        
        Returns:
            STTResult with transcription
        """
        import tempfile
        import wave
        
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
            # Write WAV file
            with wave.open(str(tmp_path), 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)
            
            # Transcribe
            result = self.transcribe_file(tmp_path)
            
            # Clean up
            try:
                tmp_path.unlink()
            except:
                pass
            
            return result
    
    def is_available(self) -> bool:
        """Check if STT is available."""
        try:
            import faster_whisper
            return True
        except ImportError:
            return False


class FallbackSTT:
    """
    Fallback STT when faster-whisper is not available.
    Returns helpful messages instead of failing silently.
    """
    
    def __init__(self):
        logger.warning("Using FallbackSTT - install faster-whisper for real STT")
    
    def initialize(self) -> bool:
        return True
    
    def transcribe_file(self, audio_path: Path) -> STTResult:
        return STTResult(
            text="[STT not available - install faster-whisper]",
            language="en",
            confidence=0.0,
            success=False
        )
    
    def transcribe_bytes(self, audio_data: bytes, sample_rate: int = 16000) -> STTResult:
        return self.transcribe_file(Path("dummy"))
    
    def is_available(self) -> bool:
        return False


def create_stt(model_size: str = "base") -> SecureSTT:
    """
    Create STT instance with automatic fallback.
    
    Args:
        model_size: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        SecureSTT or FallbackSTT instance
    """
    try:
        import faster_whisper
        return SecureSTT(model_size)
    except ImportError:
        logger.warning("faster-whisper not available, using fallback")
        return FallbackSTT()

