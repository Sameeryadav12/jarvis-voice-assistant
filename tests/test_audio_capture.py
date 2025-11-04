"""
Test script for audio capture with VU meter visualization.
Sprint 0 - Bootstrap: Demonstrates real-time mic capture.
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audio.capture import AudioCapture, create_vu_meter
from loguru import logger


def vu_meter_demo(duration: int = 10, update_interval: float = 0.1):
    """
    Run VU meter demo showing real-time audio levels.
    
    Args:
        duration: Duration to run in seconds
        update_interval: Update frequency in seconds
    """
    logger.info("Starting VU meter demo...")
    logger.info("Speak into your microphone to see the levels")
    logger.info(f"Will run for {duration} seconds")
    logger.info("-" * 60)
    
    def audio_callback(data):
        """Print VU meter on each audio chunk."""
        capture.get_rms_level(data)  # Calculate but don't print yet
    
    # Create audio capture with callback
    capture = AudioCapture(
        sample_rate=16000,
        channels=1,
        chunk_duration_ms=100,
        callback=audio_callback
    )
    
    try:
        capture.start()
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Get RMS level from recent audio
            level = capture.get_rms_level()
            
            # Create and print VU meter
            meter = create_vu_meter(level * 10, width=50)  # Scale up for visibility
            print(f"\r{meter}", end="", flush=True)
            
            time.sleep(update_interval)
        
        print()  # New line after meter
        logger.info("VU meter demo completed")
        
    except KeyboardInterrupt:
        print()
        logger.info("Demo interrupted by user")
    finally:
        capture.stop()


def list_devices_demo():
    """List all available audio devices."""
    logger.info("Available audio devices:")
    logger.info("-" * 60)
    
    devices = AudioCapture.list_devices()
    for i, device in enumerate(devices):
        name = device.get('name', 'Unknown')
        channels_in = device.get('max_input_channels', 0)
        channels_out = device.get('max_output_channels', 0)
        sample_rate = device.get('default_samplerate', 0)
        
        device_type = []
        if channels_in > 0:
            device_type.append(f"IN: {channels_in}ch")
        if channels_out > 0:
            device_type.append(f"OUT: {channels_out}ch")
        
        logger.info(
            f"[{i}] {name} | "
            f"{', '.join(device_type)} | "
            f"{sample_rate}Hz"
        )


def record_and_save_demo(duration: int = 5, output_file: str = "test_recording.wav"):
    """
    Record audio and save to WAV file.
    
    Args:
        duration: Duration to record in seconds
        output_file: Output WAV file path
    """
    import soundfile as sf
    
    logger.info(f"Recording {duration} seconds of audio...")
    
    capture = AudioCapture(sample_rate=16000, channels=1)
    
    try:
        capture.start()
        time.sleep(duration)
        capture.stop()
        
        # Get recorded audio
        audio_data = capture.get_audio_data()
        
        # Save to file
        sf.write(output_file, audio_data, capture.sample_rate)
        logger.info(f"Saved recording to {output_file}")
        logger.info(f"Duration: {len(audio_data) / capture.sample_rate:.2f}s")
        logger.info(f"Samples: {len(audio_data)}")
        
    except Exception as e:
        logger.error(f"Recording failed: {e}")
    finally:
        capture.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test audio capture functionality"
    )
    parser.add_argument(
        "--mode",
        choices=["vu", "list", "record"],
        default="vu",
        help="Test mode: vu=VU meter, list=list devices, record=save audio"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration in seconds (for vu and record modes)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_recording.wav",
        help="Output file (for record mode)"
    )
    
    args = parser.parse_args()
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    if args.mode == "vu":
        vu_meter_demo(duration=args.duration)
    elif args.mode == "list":
        list_devices_demo()
    elif args.mode == "record":
        record_and_save_demo(duration=args.duration, output_file=args.output)


if __name__ == "__main__":
    main()





