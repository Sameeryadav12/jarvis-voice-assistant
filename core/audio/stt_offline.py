"""
Offline Speech-to-Text using whisper.cpp.
Fast local speech recognition without cloud dependencies.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional
import soundfile as sf
from loguru import logger


class WhisperSTT:
    """
    Offline STT using whisper.cpp.
    Requires whisper.cpp binaries to be installed.
    """

    def __init__(
        self,
        model_path: str = "models/ggml-base.en.bin",
        whisper_bin: str = "whisper-cpp/main",
        language: str = "en",
        num_threads: int = 4
    ):
        """
        Initialize Whisper STT.
        
        Args:
            model_path: Path to GGML model file
            whisper_bin: Path to whisper.cpp binary
            language: Language code
            num_threads: Number of CPU threads
        """
        self.model_path = Path(model_path)
        self.whisper_bin = Path(whisper_bin)
        self.language = language
        self.num_threads = num_threads
        
        # Verify paths exist
        if not self.model_path.exists():
            logger.warning(f"Model not found: {model_path}")
        if not self.whisper_bin.exists():
            logger.warning(f"Whisper binary not found: {whisper_bin}")
        
        logger.info(
            f"WhisperSTT initialized: model={model_path}, "
            f"lang={language}, threads={num_threads}"
        )

    def transcribe(self, audio_data, sample_rate: int = 16000) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Audio samples (numpy array)
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
        try:
            # Save audio to temporary file
            sf.write(tmp_path, audio_data, sample_rate)
            
            # Run whisper.cpp
            result = self._run_whisper(tmp_path)
            return result
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _run_whisper(self, audio_file: str) -> str:
        """
        Run whisper.cpp binary on audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            cmd = [
                str(self.whisper_bin),
                "-m", str(self.model_path),
                "-f", audio_file,
                "-l", self.language,
                "-t", str(self.num_threads),
                "--no-timestamps",
                "--output-txt"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Whisper error: {result.stderr}")
                return ""
            
            # Parse output
            output = result.stdout.strip()
            return self._parse_output(output)
        except subprocess.TimeoutExpired:
            logger.error("Whisper transcription timed out")
            return ""
        except Exception as e:
            logger.error(f"Error running whisper: {e}")
            return ""

    def _parse_output(self, output: str) -> str:
        """
        Parse whisper.cpp output.
        
        Args:
            output: Raw output from whisper
            
        Returns:
            Cleaned transcript
        """
        # Remove timestamps and extra whitespace
        lines = output.split('\n')
        text_lines = [
            line.strip() for line in lines
            if line.strip() and not line.strip().startswith('[')
        ]
        return ' '.join(text_lines)

    @staticmethod
    def download_model(model_name: str = "base.en", models_dir: str = "models") -> bool:
        """
        Download a Whisper model (helper method).
        
        Args:
            model_name: Model name (tiny, base, small, medium, large)
            models_dir: Directory to save models
            
        Returns:
            True if successful
        """
        # This is a placeholder - actual implementation would download
        # from Hugging Face or use whisper.cpp's download script
        logger.info(f"Model download not implemented yet: {model_name}")
        logger.info("Please manually download models from:")
        logger.info("https://huggingface.co/ggerganov/whisper.cpp")
        return False


class StreamingWhisperSTT:
    """
    Streaming version of Whisper STT with chunked processing.
    Processes audio in overlapping windows for real-time transcription.
    """

    def __init__(
        self,
        whisper_stt: WhisperSTT,
        chunk_duration: float = 3.0,
        overlap: float = 0.5
    ):
        """
        Initialize streaming Whisper.
        
        Args:
            whisper_stt: WhisperSTT instance
            chunk_duration: Duration of each chunk in seconds
            overlap: Overlap between chunks (0.0-1.0)
        """
        self.whisper = whisper_stt
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        
        logger.info(
            f"StreamingWhisperSTT initialized: "
            f"chunk={chunk_duration}s, overlap={overlap}"
        )

    def transcribe_stream(self, audio_buffer, sample_rate: int = 16000) -> list:
        """
        Transcribe audio buffer in chunks.
        
        Args:
            audio_buffer: Audio buffer (numpy array)
            sample_rate: Sample rate
            
        Returns:
            List of transcriptions
        """
        chunk_size = int(self.chunk_duration * sample_rate)
        step_size = int(chunk_size * (1 - self.overlap))
        
        transcripts = []
        
        for i in range(0, len(audio_buffer) - chunk_size, step_size):
            chunk = audio_buffer[i:i + chunk_size]
            transcript = self.whisper.transcribe(chunk, sample_rate)
            if transcript:
                transcripts.append(transcript)
        
        return transcripts





