"""
Cloud Text-to-Speech using Microsoft Edge TTS.
High-quality voices via edge-tts library.
"""

import asyncio
import tempfile
import os
from typing import Optional
import sounddevice as sd
import soundfile as sf
from loguru import logger


class EdgeTTS:
    """
    Cloud TTS using Microsoft Edge voices.
    Requires internet connection but provides high-quality output.
    """

    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
        rate: str = "+0%",
        volume: str = "+0%"
    ):
        """
        Initialize Edge TTS.
        
        Args:
            voice: Voice name (e.g., 'en-US-AriaNeural', 'en-US-GuyNeural')
            rate: Speech rate adjustment (e.g., '+20%', '-10%')
            volume: Volume adjustment (e.g., '+10%', '-5%')
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        logger.info(f"EdgeTTS initialized: voice={voice}")

    async def speak_async(self, text: str, play_audio: bool = True) -> Optional[bytes]:
        """
        Convert text to speech (async).
        
        Args:
            text: Text to synthesize
            play_audio: Whether to play audio immediately
            
        Returns:
            Audio data in MP3 format, or None if error
        """
        try:
            import edge_tts
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                output_path = tmp_file.name
            
            # Generate speech
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume
            )
            await communicate.save(output_path)
            
            # Play if requested
            if play_audio:
                await self._play_audio_async(output_path)
            
            # Read audio bytes
            with open(output_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Cleanup
            os.unlink(output_path)
            
            logger.info(f"TTS: '{text[:50]}...'")
            return audio_bytes
            
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            return None
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None

    def speak(self, text: str, play_audio: bool = True) -> Optional[bytes]:
        """
        Convert text to speech (sync wrapper).
        
        Args:
            text: Text to synthesize
            play_audio: Whether to play audio immediately
            
        Returns:
            Audio data in MP3 format, or None if error
        """
        return asyncio.run(self.speak_async(text, play_audio))

    async def _play_audio_async(self, audio_file: str) -> None:
        """
        Play audio file.
        
        Args:
            audio_file: Path to audio file
        """
        try:
            # Use Windows default player (most reliable)
            import os
            logger.debug(f"Playing audio file: {audio_file}")
            if sys.platform == 'win32':
                # Use Windows Media Player
                os.system(f'start /min wmplayer "{audio_file}" /close')
            else:
                os.system(f'open "{audio_file}"')
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")

    async def save_to_file_async(self, text: str, output_file: str) -> bool:
        """
        Save TTS output to file (async).
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume
            )
            await communicate.save(output_file)
            
            logger.info(f"Saved TTS to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save TTS: {e}")
            return False

    def save_to_file(self, text: str, output_file: str) -> bool:
        """
        Save TTS output to file (sync wrapper).
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            True if successful
        """
        return asyncio.run(self.save_to_file_async(text, output_file))

    @staticmethod
    async def list_voices_async() -> list:
        """
        List available Edge TTS voices (async).
        
        Returns:
            List of voice information
        """
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return voices
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []

    @staticmethod
    def list_voices() -> list:
        """
        List available Edge TTS voices (sync wrapper).
        
        Returns:
            List of voice information
        """
        return asyncio.run(EdgeTTS.list_voices_async())


