"""
Offline Text-to-Speech using Piper.
Fast local TTS without cloud dependencies.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional
import sounddevice as sd
import soundfile as sf
from loguru import logger


class PiperTTS:
    """
    Offline TTS using Piper.
    Requires Piper binary and voice models.
    """

    def __init__(
        self,
        model_path: str = "models/piper/en_US-lessac-medium.onnx",
        piper_bin: str = "piper/piper",
        sample_rate: int = 22050
    ):
        """
        Initialize Piper TTS.
        
        Args:
            model_path: Path to Piper ONNX model
            piper_bin: Path to Piper binary
            sample_rate: Audio sample rate
        """
        self.model_path = Path(model_path)
        self.piper_bin = Path(piper_bin)
        self.sample_rate = sample_rate
        
        if not self.model_path.exists():
            logger.warning(f"Piper model not found: {model_path}")
        if not self.piper_bin.exists():
            logger.warning(f"Piper binary not found: {piper_bin}")
        
        logger.info(f"PiperTTS initialized: model={model_path}")

    def speak(self, text: str, play_audio: bool = True) -> Optional[bytes]:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            play_audio: Whether to play audio immediately
            
        Returns:
            Audio data in WAV format, or None if error
        """
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
            
            # Run Piper
            self._run_piper(text, output_path)
            
            # Read audio data
            audio_data, sr = sf.read(output_path, dtype='float32')
            
            # Play if requested
            if play_audio:
                self._play_audio(audio_data, sr)
            
            # Read WAV bytes
            with open(output_path, 'rb') as f:
                wav_bytes = f.read()
            
            # Cleanup
            os.unlink(output_path)
            
            logger.info(f"TTS: '{text[:50]}...'")
            return wav_bytes
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None

    def _run_piper(self, text: str, output_file: str) -> None:
        """
        Run Piper binary to generate speech.
        
        Args:
            text: Text to synthesize
            output_file: Output WAV file path
        """
        cmd = [
            str(self.piper_bin),
            "--model", str(self.model_path),
            "--output_file", output_file
        ]
        
        result = subprocess.run(
            cmd,
            input=text.encode('utf-8'),
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Piper error: {result.stderr.decode()}")

    def _play_audio(self, audio_data, sample_rate: int) -> None:
        """
        Play audio data.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
        """
        sd.play(audio_data, sample_rate)
        sd.wait()

    def save_to_file(self, text: str, output_file: str) -> bool:
        """
        Save TTS output to file.
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            self._run_piper(text, output_file)
            logger.info(f"Saved TTS to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save TTS: {e}")
            return False

    @staticmethod
    def list_available_models() -> list:
        """
        List available Piper voice models.
        
        Returns:
            List of model paths
        """
        # This would scan a models directory
        # Placeholder implementation
        logger.info("Model listing not implemented yet")
        return []





