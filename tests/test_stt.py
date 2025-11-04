"""
Test script for speech-to-text functionality.
Tests both offline (whisper.cpp) and cloud (OpenAI) modes.
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audio.capture import AudioCapture
from core.audio.stt_offline import WhisperSTT
from loguru import logger
import numpy as np


def test_offline_stt(
    model_path: str,
    whisper_bin: str,
    duration: int = 5
):
    """
    Test offline STT with whisper.cpp.
    
    Args:
        model_path: Path to GGML model
        whisper_bin: Path to whisper binary
        duration: Recording duration in seconds
    """
    logger.info("=" * 60)
    logger.info("Offline STT Test (whisper.cpp)")
    logger.info("=" * 60)
    logger.info(f"Model: {model_path}")
    logger.info(f"Binary: {whisper_bin}")
    logger.info(f"Duration: {duration} seconds")
    logger.info("")
    
    try:
        # Check if model exists
        if not Path(model_path).exists():
            logger.error(f"Model not found: {model_path}")
            logger.info("Download models from:")
            logger.info("https://huggingface.co/ggerganov/whisper.cpp")
            return False
        
        # Check if binary exists
        if not Path(whisper_bin).exists():
            logger.warning(f"Whisper binary not found: {whisper_bin}")
            logger.info("Build whisper.cpp or adjust path")
        
        # Initialize STT
        stt = WhisperSTT(
            model_path=model_path,
            whisper_bin=whisper_bin
        )
        
        # Record audio
        logger.info("Recording... Speak now!")
        logger.info("-" * 60)
        
        capture = AudioCapture(sample_rate=16000, channels=1)
        capture.start()
        
        # Show VU meter while recording
        start_time = time.time()
        while time.time() - start_time < duration:
            level = capture.get_rms_level()
            from core.audio.capture import create_vu_meter
            meter = create_vu_meter(level * 10, width=40)
            print(f"\r{meter}", end="", flush=True)
            time.sleep(0.1)
        
        print()  # New line
        
        # Get audio data
        audio_data = capture.get_audio_data()
        capture.stop()
        
        logger.info(f"Recorded {len(audio_data)} samples")
        logger.info("Transcribing...")
        logger.info("")
        
        # Transcribe
        transcript = stt.transcribe(audio_data, sample_rate=16000)
        
        logger.info("=" * 60)
        logger.info("TRANSCRIPT:")
        logger.info(transcript if transcript else "(empty)")
        logger.info("=" * 60)
        
        return bool(transcript)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cloud_stt(api_key: str, test_text: str = "Hello Jarvis"):
    """
    Test cloud STT with OpenAI Realtime API.
    
    Args:
        api_key: OpenAI API key
        test_text: Text to speak for testing
    """
    logger.info("=" * 60)
    logger.info("Cloud STT Test (OpenAI Realtime API)")
    logger.info("=" * 60)
    logger.info("Note: Full implementation requires async WebSocket")
    logger.info("This is a simplified test")
    logger.info("")
    
    try:
        from core.audio.stt_realtime import RealtimeSTT
        import asyncio
        
        transcript_received = False
        
        def on_transcript(text: str):
            nonlocal transcript_received
            logger.info(f"Transcript: {text}")
            transcript_received = True
        
        async def test():
            async with RealtimeSTT(
                api_key=api_key,
                on_transcript=on_transcript
            ) as stt:
                logger.info("Connected to OpenAI Realtime API")
                # In a full implementation, we'd send audio here
                # For now, just test connection
                await asyncio.sleep(2)
        
        asyncio.run(test())
        
        logger.info("Cloud STT test complete")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test speech-to-text functionality"
    )
    parser.add_argument(
        "--mode",
        choices=["offline", "cloud"],
        default="offline",
        help="STT mode to test"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/ggml-base.en.bin",
        help="Path to Whisper GGML model (offline mode)"
    )
    parser.add_argument(
        "--whisper-bin",
        type=str,
        default="whisper-cpp/main",
        help="Path to whisper.cpp binary (offline mode)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (cloud mode)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Recording duration in seconds (offline mode)"
    )
    
    args = parser.parse_args()
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Run appropriate test
    if args.mode == "offline":
        success = test_offline_stt(
            model_path=args.model_path,
            whisper_bin=args.whisper_bin,
            duration=args.duration
        )
    else:
        if not args.api_key:
            logger.error("OpenAI API key required for cloud mode")
            logger.info("Use --api-key YOUR_KEY")
            sys.exit(1)
        
        success = test_cloud_stt(api_key=args.api_key)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()





