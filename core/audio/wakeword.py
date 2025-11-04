"""
Wake word detection using Picovoice Porcupine.
Detects "Hey Jarvis" or custom wake words.
"""

import struct
from typing import Optional, Callable
import pvporcupine
from loguru import logger


class WakeWordDetector:
    """
    Wake word detection using Porcupine.
    Processes audio frames and triggers callback on detection.
    """

    def __init__(
        self,
        access_key: str,
        keyword_paths: Optional[list] = None,
        keywords: Optional[list] = None,
        sensitivities: Optional[list] = None,
        callback: Optional[Callable[[int], None]] = None
    ):
        """
        Initialize wake word detector.
        
        Args:
            access_key: Picovoice access key (get from console.picovoice.ai)
            keyword_paths: Paths to custom .ppn keyword files
            keywords: Built-in keywords (e.g., ['jarvis', 'computer'])
            sensitivities: Detection sensitivity per keyword (0.0-1.0)
            callback: Function called when wake word detected (receives keyword_index)
        """
        self.access_key = access_key
        self.callback = callback
        
        # Use keywords or keyword_paths
        if keywords is None and keyword_paths is None:
            keywords = ["jarvis"]  # Default wake word
        
        # Set default sensitivities
        num_keywords = len(keywords) if keywords else len(keyword_paths)
        if sensitivities is None:
            sensitivities = [0.5] * num_keywords
        
        try:
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=keyword_paths,
                keywords=keywords,
                sensitivities=sensitivities
            )
            
            self.sample_rate = self.porcupine.sample_rate
            self.frame_length = self.porcupine.frame_length
            
            logger.info(
                f"WakeWordDetector initialized: "
                f"keywords={keywords or 'custom'}, "
                f"sample_rate={self.sample_rate}Hz, "
                f"frame_length={self.frame_length}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            raise

    def process_frame(self, audio_frame) -> int:
        """
        Process a single audio frame for wake word detection.
        
        Args:
            audio_frame: Audio frame (must match frame_length)
            
        Returns:
            Keyword index if detected (>= 0), -1 otherwise
        """
        try:
            # Convert float32 audio to int16 for Porcupine
            if audio_frame.dtype != 'int16':
                audio_frame = (audio_frame * 32767).astype('int16')
            
            keyword_index = self.porcupine.process(audio_frame)
            
            if keyword_index >= 0:
                logger.info(f"Wake word detected! Index: {keyword_index}")
                if self.callback:
                    self.callback(keyword_index)
            
            return keyword_index
        except Exception as e:
            logger.error(f"Error processing wake word frame: {e}")
            return -1

    def delete(self) -> None:
        """Release Porcupine resources."""
        if self.porcupine:
            self.porcupine.delete()
            logger.debug("Porcupine resources released")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.delete()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.delete()


class WakeWordConfig:
    """Configuration for wake word detection."""
    
    def __init__(
        self,
        access_key: str = "",
        keyword: str = "jarvis",
        sensitivity: float = 0.5,
        enabled: bool = True
    ):
        """
        Initialize wake word configuration.
        
        Args:
            access_key: Picovoice access key
            keyword: Wake word to detect
            sensitivity: Detection sensitivity (0.0-1.0)
            enabled: Whether wake word detection is enabled
        """
        self.access_key = access_key
        self.keyword = keyword
        self.sensitivity = sensitivity
        self.enabled = enabled

    @classmethod
    def from_dict(cls, config: dict) -> "WakeWordConfig":
        """Create config from dictionary."""
        return cls(**config)

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "access_key": self.access_key,
            "keyword": self.keyword,
            "sensitivity": self.sensitivity,
            "enabled": self.enabled
        }





