"""
Test script for complete audio pipeline.
Tests: audio capture → wake word → STT → transcript
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audio.audio_pipeline import AudioPipeline, PipelineState
from loguru import logger


def test_pipeline(config: dict, duration: int = 60):
    """
    Test complete audio pipeline.
    
    Args:
        config: Pipeline configuration
        duration: Test duration in seconds
    """
    logger.info("=" * 60)
    logger.info("Audio Pipeline Integration Test")
    logger.info("=" * 60)
    logger.info(f"STT Mode: {config['stt_mode']}")
    logger.info(f"Wake Word: {config.get('wake_word', {}).get('keyword', 'N/A')}")
    logger.info(f"Duration: {duration} seconds")
    logger.info("")
    logger.info("Say the wake word, then speak a command")
    logger.info("-" * 60)
    logger.info("")
    
    transcripts = []
    state_changes = []
    
    def on_transcript(text: str):
        """Callback for transcripts."""
        logger.info("🎤 TRANSCRIPT:")
        logger.info(f"   {text}")
        logger.info("")
        transcripts.append(text)
    
    def on_state_change(state: PipelineState):
        """Callback for state changes."""
        state_changes.append(state)
        
        if state == PipelineState.LISTENING:
            logger.info("👂 Listening for wake word...")
        elif state == PipelineState.WAKE_WORD_DETECTED:
            logger.info("✅ Wake word detected!")
        elif state == PipelineState.PROCESSING_SPEECH:
            logger.info("🗣️ Listening to your command...")
        elif state == PipelineState.ERROR:
            logger.error("❌ Pipeline error")
    
    try:
        # Create pipeline
        pipeline = AudioPipeline(
            stt_mode=config["stt_mode"],
            wake_word_config=config.get("wake_word", {}),
            stt_config=config.get("stt", {}),
            on_transcript=on_transcript,
            on_state_change=on_state_change
        )
        
        # Start pipeline
        pipeline.start()
        
        # Run for specified duration
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("\nStopped by user")
        
        # Stop pipeline
        pipeline.stop()
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Transcripts received: {len(transcripts)}")
        logger.info(f"State changes: {len(state_changes)}")
        
        if transcripts:
            logger.info("")
            logger.info("Transcripts:")
            for i, t in enumerate(transcripts, 1):
                logger.info(f"  {i}. {t}")
        
        logger.info("=" * 60)
        
        return len(transcripts) > 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test complete audio pipeline"
    )
    parser.add_argument(
        "--stt-mode",
        choices=["offline", "cloud"],
        default="offline",
        help="STT mode"
    )
    parser.add_argument(
        "--wake-word-key",
        type=str,
        help="Picovoice access key for wake word detection"
    )
    parser.add_argument(
        "--wake-word",
        type=str,
        default="jarvis",
        help="Wake word keyword"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/ggml-base.en.bin",
        help="Path to Whisper model (offline mode)"
    )
    parser.add_argument(
        "--whisper-bin",
        type=str,
        default="whisper-cpp/main",
        help="Path to whisper.cpp binary (offline mode)"
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        help="OpenAI API key (cloud mode)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds"
    )
    parser.add_argument(
        "--no-wake-word",
        action="store_true",
        help="Skip wake word detection (process all speech)"
    )
    
    args = parser.parse_args()
    
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Build configuration
    config = {
        "stt_mode": args.stt_mode,
        "wake_word": {} if args.no_wake_word else {
            "access_key": args.wake_word_key or "",
            "keyword": args.wake_word,
            "sensitivity": 0.5
        },
        "stt": {}
    }
    
    if args.stt_mode == "offline":
        config["stt"] = {
            "model_path": args.model_path,
            "binary_path": args.whisper_bin
        }
    else:
        config["stt"] = {
            "api_key": args.openai_key or ""
        }
    
    # Validate configuration
    if not args.no_wake_word and not args.wake_word_key:
        logger.warning("No Picovoice key provided. Wake word detection disabled.")
        logger.info("Get a free key at: https://console.picovoice.ai")
        config["wake_word"] = {}
    
    if args.stt_mode == "offline":
        if not Path(args.model_path).exists():
            logger.warning(f"Whisper model not found: {args.model_path}")
            logger.info("Download from: https://huggingface.co/ggerganov/whisper.cpp")
    else:
        if not args.openai_key:
            logger.error("OpenAI API key required for cloud mode")
            sys.exit(1)
    
    # Run test
    success = test_pipeline(config, duration=args.duration)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()





