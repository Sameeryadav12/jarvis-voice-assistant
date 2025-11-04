"""
Secure Text-to-Speech Handler
Uses edge-tts (Microsoft) - secure, high-quality, free
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)


class SecureTTS:
    """
    Secure TTS using edge-tts (Microsoft Edge's neural voices).
    Free, high-quality, and privacy-respecting.
    """
    
    def __init__(self, voice: str = "en-US-AriaNeural"):
        """
        Initialize TTS.
        
        Args:
            voice: Voice name. Popular options:
                   - en-US-AriaNeural (female, clear)
                   - en-US-GuyNeural (male, natural)
                   - en-US-JennyNeural (female, friendly)
                   - en-GB-SoniaNeural (British female)
        """
        self.voice = voice
        self.is_speaking = False
        
        logger.info(f"Initialized SecureTTS with voice: {voice}")
    
    async def speak_async(self, text: str, output_file: Optional[Path] = None) -> bool:
        """
        Convert text to speech (async).
        
        Args:
            text: Text to speak
            output_file: Optional output file path. If None, uses temp file.
        
        Returns:
            True if successful
        """
        if not text.strip():
            logger.warning("Empty text provided")
            return False
        
        try:
            import edge_tts
            import pygame
            
            # Create temporary file if no output specified
            if output_file is None:
                tmp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                output_file = Path(tmp_file.name)
                tmp_file.close()
                is_temp = True
            else:
                is_temp = False
            
            logger.info(f"Generating speech: '{text[:50]}...'")
            
            # Generate speech using edge-tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(output_file))
            
            logger.info(f"Speech generated: {output_file}")
            
            # Play the audio using pygame
            self.is_speaking = True
            
            try:
                # Initialize pygame mixer
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                # Load and play
                pygame.mixer.music.load(str(output_file))
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                logger.info("Playback complete")
                
            finally:
                self.is_speaking = False
                
                # Clean up temp file
                if is_temp:
                    try:
                        output_file.unlink()
                    except:
                        pass
            
            return True
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}. Install with: pip install edge-tts pygame")
            return False
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            self.is_speaking = False
            return False
    
    def speak(self, text: str, output_file: Optional[Path] = None) -> bool:
        """
        Convert text to speech (sync wrapper).
        
        Args:
            text: Text to speak
            output_file: Optional output file path
        
        Returns:
            True if successful
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.speak_async(text, output_file))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"TTS sync failed: {e}")
            return False
    
    def stop(self):
        """Stop current speech."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            self.is_speaking = False
            logger.info("Stopped speech")
        except:
            pass
    
    @staticmethod
    def list_voices():
        """List available voices."""
        try:
            import edge_tts
            
            async def get_voices():
                voices = await edge_tts.list_voices()
                return voices
            
            loop = asyncio.new_event_loop()
            voices = loop.run_until_complete(get_voices())
            loop.close()
            
            # Filter English voices
            english_voices = [
                v for v in voices 
                if v['Locale'].startswith('en-')
            ]
            
            return english_voices
            
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []
    
    @staticmethod
    def is_available() -> bool:
        """Check if TTS is available."""
        try:
            import edge_tts
            import pygame
            return True
        except ImportError:
            return False


class FallbackTTS:
    """Fallback TTS when edge-tts is not available."""
    
    def __init__(self):
        logger.warning("Using FallbackTTS - install edge-tts and pygame for real TTS")
        self.is_speaking = False
    
    def speak(self, text: str, output_file: Optional[Path] = None) -> bool:
        logger.info(f"[TTS NOT AVAILABLE] Would speak: '{text}'")
        return False
    
    async def speak_async(self, text: str, output_file: Optional[Path] = None) -> bool:
        return self.speak(text, output_file)
    
    def stop(self):
        pass
    
    @staticmethod
    def list_voices():
        return []
    
    @staticmethod
    def is_available() -> bool:
        return False


def create_tts(voice: str = "en-US-AriaNeural") -> SecureTTS:
    """
    Create TTS instance with automatic fallback.
    
    Args:
        voice: Voice name
    
    Returns:
        SecureTTS or FallbackTTS instance
    """
    if SecureTTS.is_available():
        return SecureTTS(voice)
    else:
        logger.warning("edge-tts or pygame not available, using fallback")
        return FallbackTTS()

