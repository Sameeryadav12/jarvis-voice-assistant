"""
Secure Voice Manager
Handles audio input/output with trusted libraries
"""

import logging
import threading
import queue
import numpy as np
from pathlib import Path
from typing import Optional, Callable
import tempfile

logger = logging.getLogger(__name__)


class VoiceInputManager:
    """
    Secure microphone input manager.
    Uses sounddevice (trusted, BSD-licensed) for audio capture.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize voice input manager.
        
        Args:
            sample_rate: Audio sample rate (16kHz recommended for speech)
        """
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread: Optional[threading.Thread] = None
        
        # Lazy import to avoid dependency issues
        try:
            import sounddevice as sd
            self.sd = sd
            self.available = True
            logger.info("Voice input initialized with sounddevice")
        except ImportError:
            logger.warning("sounddevice not available - voice input disabled")
            self.available = False
    
    def start_recording(self) -> bool:
        """
        Start recording audio from microphone.
        
        Returns:
            True if recording started successfully
        """
        if not self.available:
            logger.error("Voice input not available")
            return False
        
        if self.is_recording:
            logger.warning("Already recording")
            return False
        
        try:
            self.is_recording = True
            self.audio_queue = queue.Queue()
            
            # Start recording in background thread
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                daemon=True
            )
            self.recording_thread.start()
            
            logger.info("Recording started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording and return audio data.
        
        Returns:
            Audio data as numpy array, or None if failed
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        
        # Collect all audio chunks
        audio_chunks = []
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                audio_chunks.append(chunk)
            except queue.Empty:
                break
        
        if not audio_chunks:
            logger.warning("No audio recorded")
            return None
        
        # Concatenate chunks
        audio_data = np.concatenate(audio_chunks, axis=0)
        logger.info(f"Recording stopped - {len(audio_data)} samples captured")
        
        return audio_data
    
    def _record_audio(self):
        """Background thread for audio recording."""
        try:
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Recording status: {status}")
                if self.is_recording:
                    self.audio_queue.put(indata.copy())
            
            with self.sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=callback
            ):
                while self.is_recording:
                    self.sd.sleep(100)
                    
        except Exception as e:
            logger.error(f"Recording error: {e}")
            self.is_recording = False


class SpeechToTextManager:
    """
    Secure Speech-to-Text using faster-whisper.
    Uses CTranslate2 (MIT licensed) for efficient inference.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize STT manager.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.available = False
        
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )
            self.available = True
            logger.info("STT initialized successfully")
            
        except ImportError:
            logger.warning("faster-whisper not available - STT disabled")
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
    
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio
        
        Returns:
            Transcribed text, or None if failed
        """
        if not self.available or self.model is None:
            logger.error("STT not available")
            return None
        
        try:
            # Ensure audio is in correct format
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()
            
            # Normalize audio
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_data,
                language="en",
                beam_size=5,
                vad_filter=True
            )
            
            # Collect all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            result = " ".join(text_parts).strip()
            
            if result:
                logger.info(f"Transcribed: '{result}'")
                return result
            else:
                logger.warning("No speech detected")
                return None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None


class TextToSpeechManager:
    """
    Secure Text-to-Speech using edge-tts.
    Uses Microsoft's Edge TTS service (free, no API key required).
    """
    
    def __init__(self, voice: str = "en-US-AriaNeural"):
        """
        Initialize TTS manager.
        
        Args:
            voice: Voice to use for TTS
        """
        self.voice = voice
        self.available = False
        
        try:
            import edge_tts
            import asyncio
            self.edge_tts = edge_tts
            self.asyncio = asyncio
            self.available = True
            logger.info(f"TTS initialized with voice: {voice}")
            
        except ImportError:
            logger.warning("edge-tts not available - TTS disabled")
    
    def speak(self, text: str, callback: Optional[Callable] = None) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            callback: Optional callback when speech is done
        
        Returns:
            True if successful
        """
        if not self.available:
            logger.error("TTS not available")
            return False
        
        if not text.strip():
            logger.warning("Empty text provided")
            return False
        
        try:
            # Run async TTS in thread
            thread = threading.Thread(
                target=self._speak_async,
                args=(text, callback),
                daemon=True
            )
            thread.start()
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _speak_async(self, text: str, callback: Optional[Callable]):
        """Async TTS implementation."""
        try:
            # Create new event loop for this thread
            loop = self.asyncio.new_event_loop()
            self.asyncio.set_event_loop(loop)
            
            # Run TTS
            loop.run_until_complete(self._do_tts(text))
            
            # Callback
            if callback:
                callback()
                
        except Exception as e:
            logger.error(f"Async TTS error: {e}")
        finally:
            loop.close()
    
    async def _do_tts(self, text: str):
        """Perform TTS and play audio."""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            communicate = self.edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_path)
            
            # Play audio
            await self._play_audio(temp_path)
            
            # Clean up
            try:
                Path(temp_path).unlink()
            except:
                pass
                
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
    
    async def _play_audio(self, audio_path: str):
        """Play audio file."""
        try:
            import sounddevice as sd
            import soundfile as sf
            
            # Read audio file
            data, samplerate = sf.read(audio_path)
            
            # Play audio
            sd.play(data, samplerate)
            sd.wait()
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            # Fallback: try system player
            try:
                import os
                if os.name == 'nt':
                    os.system(f'start "" "{audio_path}"')
            except:
                pass


class VoiceManager:
    """
    Complete voice interaction manager.
    Combines input, STT, and TTS for full voice pipeline.
    """
    
    def __init__(
        self,
        stt_model: str = "base",
        tts_voice: str = "en-US-AriaNeural"
    ):
        """
        Initialize complete voice manager.
        
        Args:
            stt_model: Whisper model size for STT
            tts_voice: Voice to use for TTS
        """
        logger.info("Initializing Voice Manager...")
        
        self.input_manager = VoiceInputManager()
        self.stt_manager = SpeechToTextManager(stt_model)
        self.tts_manager = TextToSpeechManager(tts_voice)
        
        # Check availability
        self.voice_input_available = self.input_manager.available
        self.stt_available = self.stt_manager.available
        self.tts_available = self.tts_manager.available
        
        logger.info(f"Voice Manager initialized - Input: {self.voice_input_available}, STT: {self.stt_available}, TTS: {self.tts_available}")
    
    def start_listening(self) -> bool:
        """Start listening for voice input."""
        return self.input_manager.start_recording()
    
    def stop_listening(self) -> Optional[str]:
        """
        Stop listening and transcribe audio.
        
        Returns:
            Transcribed text, or None if failed
        """
        audio_data = self.input_manager.stop_recording()
        
        if audio_data is None:
            return None
        
        return self.stt_manager.transcribe(audio_data)
    
    def speak(self, text: str, callback: Optional[Callable] = None) -> bool:
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            callback: Optional callback when done
        
        Returns:
            True if successful
        """
        return self.tts_manager.speak(text, callback)
    
    def is_available(self) -> bool:
        """Check if voice features are available."""
        return (
            self.voice_input_available and
            self.stt_available and
            self.tts_available
        )

