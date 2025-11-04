"""
Test script for wake word detection.
Requires Picovoice access key.
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audio.capture import AudioCapture
from core.audio.wakeword import WakeWordDetector
from loguru import logger


def test_wake_word(access_key: str, keyword: str = "jarvis", duration: int = 30):
    """
    Test wake word detection.
    
    Args:
        access_key: Picovoice access key
        keyword: Keyword to detect
        duration: Test duration in seconds
    """
    logger.info("=" * 60)
    logger.info("Wake Word Detection Test")
    logger.info("=" * 60)
    logger.info(f"Keyword: {keyword}")
    logger.info(f"Duration: {duration} seconds")
    logger.info("Say the wake word to test detection!")
    logger.info("-" * 60)
    
    detected_count = 0
    
    def on_wake_word(keyword_index: int):
        """Callback when wake word detected."""
        nonlocal detected_count
        detected_count += 1
        logger.info(f"🎤 WAKE WORD DETECTED! (#{detected_count})")
    
    try:
        # Initialize wake word detector
        detector = WakeWordDetector(
            access_key=access_key,
            keywords=[keyword],
            sensitivities=[0.5],
            callback=on_wake_word
        )
        
        logger.info(f"Sample rate: {detector.sample_rate}Hz")
        logger.info(f"Frame length: {detector.frame_length} samples")
        logger.info("")
        
        # Initialize audio capture
        # Note: Porcupine requires specific sample rate
        capture = AudioCapture(
            sample_rate=detector.sample_rate,
            channels=1,
            chunk_duration_ms=30
        )
        
        # Callback to process audio frames
        def audio_callback(data):
            # Convert float32 to int16 for Porcupine
            import numpy as np
            audio_int16 = (data * 32767).astype(np.int16)
            
            # Process in chunks of frame_length
            for i in range(0, len(audio_int16), detector.frame_length):
                frame = audio_int16[i:i + detector.frame_length]
                if len(frame) == detector.frame_length:
                    detector.process_frame(frame)
        
        capture.callback = audio_callback
        
        # Start capturing
        capture.start()
        
        logger.info("Listening... (Press Ctrl+C to stop)")
        logger.info("")
        
        # Run for specified duration
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("\nStopped by user")
        
        # Stop capture
        capture.stop()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"Test complete! Detected {detected_count} time(s)")
        logger.info("=" * 60)
        
        return detected_count > 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test wake word detection"
    )
    parser.add_argument(
        "--access-key",
        type=str,
        required=True,
        help="Picovoice access key (get from console.picovoice.ai)"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="jarvis",
        help="Wake word keyword (default: jarvis)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Test duration in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Run test
    success = test_wake_word(
        access_key=args.access_key,
        keyword=args.keyword,
        duration=args.duration
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()





