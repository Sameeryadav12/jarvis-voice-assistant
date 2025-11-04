"""
Simple reliable TTS for Jarvis UI
"""
import asyncio
import edge_tts
import pygame
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SimpleTTS:
    """Simple TTS using edge-tts and pygame."""
    
    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice
        pygame.mixer.init()
        logger.info(f"SimpleTTS initialized: {voice}")
    
    def speak(self, text):
        """Speak text (synchronous)."""
        try:
            if not text.strip():
                return False
            
            logger.info(f"Speaking: {text[:50]}...")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate speech
            asyncio.run(self._generate_speech(text, tmp_path))
            
            # Play audio
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            # Wait for completion
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Cleanup
            try:
                Path(tmp_path).unlink()
            except:
                pass
            
            logger.info("Speech complete")
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    async def _generate_speech(self, text, output_path):
        """Generate speech file."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
    
    def is_available(self):
        """Check if TTS is available."""
        return True


def test_tts():
    """Test TTS."""
    tts = SimpleTTS()
    print("Testing TTS...")
    tts.speak("Hello! This is a test of the text to speech system.")
    print("Done!")


if __name__ == "__main__":
    test_tts()

