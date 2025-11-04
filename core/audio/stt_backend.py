"""
STT Backend Strategy Pattern

Allows hot-swapping of STT backends without code changes.
Supports multiple STT providers (whisper.cpp, faster-whisper, OpenAI, etc.)
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union
import numpy as np
from loguru import logger


class STTBackendType(Enum):
    """Available STT backend types."""
    WHISPER_CPP = "whisper_cpp"
    FASTER_WHISPER = "faster_whisper"
    OPENAI_REALTIME = "openai_realtime"
    CLOUD_STT = "cloud_stt"


class STTBackend(ABC):
    """
    Abstract base class for STT backends.
    All STT implementations must inherit from this class.
    """
    
    @abstractmethod
    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            language: Language code (or None for auto-detect)
            
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def transcribe_stream(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000,
    ) -> Optional[str]:
        """
        Transcribe a single audio chunk (streaming mode).
        
        Args:
            audio_chunk: Audio chunk as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            Transcribed text or None if not ready
        """
        pass
    
    @abstractmethod
    def get_backend_info(self) -> dict:
        """Get backend information."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available."""
        pass


class STTBackendManager:
    """
    Manages multiple STT backends and allows hot-swapping.
    """
    
    def __init__(
        self,
        default_backend: STTBackendType = STTBackendType.FASTER_WHISPER,
        **backend_config
    ):
        """
        Initialize STT backend manager.
        
        Args:
            default_backend: Default backend type to use
            **backend_config: Configuration for specific backends
        """
        self.default_backend_type = default_backend
        self.backend_config = backend_config
        self.current_backend: Optional[STTBackend] = None
        self.available_backends: dict[str, STTBackendType] = {}
        
        # Initialize backend
        self._initialize_backend(default_backend)
    
    def _initialize_backend(self, backend_type: STTBackendType):
        """Initialize a specific backend."""
        logger.info(f"Initializing STT backend: {backend_type.value}")
        
        try:
            if backend_type == STTBackendType.FASTER_WHISPER:
                from .stt_faster_whisper import create_faster_whisper
                config = self.backend_config.get('faster_whisper', {})
                self.current_backend = create_faster_whisper(**config)
                
            elif backend_type == STTBackendType.WHISPER_CPP:
                from .stt_offline import WhisperSTT
                config = self.backend_config.get('whisper_cpp', {})
                self.current_backend = WhisperSTT(**config)
                
            elif backend_type == STTBackendType.OPENAI_REALTIME:
                from .stt_realtime import RealtimeSTT
                config = self.backend_config.get('openai_realtime', {})
                self.current_backend = RealtimeSTT(**config)
                
            else:
                logger.error(f"Unknown backend type: {backend_type}")
                self.current_backend = None
            
            if self.current_backend and self.current_backend.is_available():
                logger.info(f"STT backend initialized: {backend_type.value}")
                self.available_backends[backend_type.value] = backend_type
            else:
                logger.warning(f"STT backend not available: {backend_type.value}")
                self.current_backend = None
                
        except Exception as e:
            logger.error(f"Failed to initialize STT backend: {e}")
            self.current_backend = None
    
    def switch_backend(self, backend_type: STTBackendType) -> bool:
        """
        Switch to a different backend.
        
        Args:
            backend_type: Backend type to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        logger.info(f"Switching STT backend to: {backend_type.value}")
        
        # Check if already using this backend
        if (self.current_backend and 
            backend_type == self.default_backend_type):
            logger.info("Already using this backend")
            return True
        
        # Initialize new backend
        self._initialize_backend(backend_type)
        
        if self.current_backend and self.current_backend.is_available():
            self.default_backend_type = backend_type
            logger.info(f"Switched to backend: {backend_type.value}")
            return True
        else:
            logger.error(f"Failed to switch to backend: {backend_type.value}")
            return False
    
    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio using current backend.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            language: Language code
            
        Returns:
            Transcribed text
        """
        if not self.current_backend:
            logger.error("No STT backend available")
            return ""
        
        try:
            return self.current_backend.transcribe(
                audio_data,
                sample_rate,
                language
            )
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    def transcribe_stream(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000,
    ) -> Optional[str]:
        """
        Transcribe audio chunk using current backend (streaming).
        
        Args:
            audio_chunk: Audio chunk as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            Transcribed text or None
        """
        if not self.current_backend:
            return None
        
        try:
            return self.current_backend.transcribe_stream(
                audio_chunk,
                sample_rate
            )
        except Exception as e:
            logger.error(f"Stream transcription failed: {e}")
            return None
    
    def get_backend_info(self) -> dict:
        """Get current backend information."""
        if not self.current_backend:
            return {
                "backend": "none",
                "available": False,
            }
        
        info = self.current_backend.get_backend_info()
        info["type"] = self.default_backend_type.value
        return info
    
    def list_available_backends(self) -> list[str]:
        """List all available backends."""
        return list(self.available_backends.keys())
    
    def is_available(self) -> bool:
        """Check if any backend is available."""
        return self.current_backend is not None and self.current_backend.is_available()
    
    def __repr__(self) -> str:
        """String representation."""
        backend_name = (
            self.default_backend_type.value 
            if self.current_backend else "none"
        )
        return f"STTBackendManager(backend={backend_name})"


# Factory function
def create_stt_backend_manager(
    backend_type: str = "faster_whisper",
    **config
) -> Optional[STTBackendManager]:
    """
    Create an STT backend manager.
    
    Args:
        backend_type: Backend type ("faster_whisper", "whisper_cpp", "openai_realtime")
        **config: Backend-specific configuration
        
    Returns:
        STTBackendManager instance or None if creation failed
    """
    try:
        backend_enum = STTBackendType(backend_type)
        manager = STTBackendManager(backend_enum, **config)
        
        if manager.is_available():
            return manager
        else:
            logger.warning("STT backend manager created but no backend available")
            return None
            
    except ValueError:
        logger.error(f"Invalid backend type: {backend_type}")
        return None
    except Exception as e:
        logger.error(f"Failed to create STT backend manager: {e}")
        return None


# Test function
if __name__ == "__main__":
    import sounddevice as sd
    import time
    
    logger.info("Testing STT Backend Manager...")
    
    # Create manager with faster-whisper
    manager = create_stt_backend_manager(
        backend_type="faster_whisper",
        faster_whisper={"model_size": "tiny"}
    )
    
    if manager:
        print(f"Available backends: {manager.list_available_backends()}")
        print(f"Manager: {manager}")
        
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
        transcript = manager.transcribe(audio_data[:, 0], sample_rate)
        elapsed = time.time() - start_time
        
        print(f"Transcribed in {elapsed:.2f}s:")
        print(f"'{transcript}'")
        
        # Test backend switching
        print("\nTesting backend switch...")
        # (Would need to initialize whisper_cpp separately)
        
    else:
        print("Manager not available")

