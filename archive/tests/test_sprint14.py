"""
Test Sprint 14: Speech Excellence Features

Tests:
- S14-01: VAD Microphone Profile Detection
- S14-02: Partial Result Captions
- S14-03: Barge-In (Interrupt TTS)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
import numpy as np
import sounddevice as sd
import time

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def test_vad_profiles():
    """Test S14-01: VAD Microphone Profile Detection."""
    print("\n" + "=" * 60)
    print("TEST S14-01: VAD Microphone Profile Detection")
    print("=" * 60)
    
    try:
        from core.audio.vad_profiles import VADProfiler, create_default_profiler
        
        print("\n[1/3] Creating VAD profiler...")
        profiler = create_default_profiler()
        print("  [OK] VAD profiler created")
        
        print("\n[2/3] Creating microphone profile...")
        device_id = sd.default.device[0]
        profile = profiler.create_profile(device_id=device_id, calibration_duration=1.0)
        print(f"  [OK] Profile created:")
        print(f"    Device: {profile.device_name}")
        print(f"    Threshold: {profile.threshold:.3f}")
        print(f"    Noise Level: {profile.noise_level:.3f}")
        print(f"    Sensitivity: {profile.sensitivity:.3f}")
        
        print("\n[3/3] Testing profile retrieval...")
        retrieved_profile = profiler.get_profile(device_id=device_id)
        assert retrieved_profile is not None
        assert retrieved_profile.device_id == device_id
        print(f"  [OK] Profile retrieved successfully")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S14-01: VAD Profiles - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_partial_results():
    """Test S14-02: Partial Result Captions."""
    print("\n" + "=" * 60)
    print("TEST S14-02: Partial Result Captions")
    print("=" * 60)
    
    try:
        from core.audio.stt_partial import (
            FasterWhisperPartialStreamer,
            PartialResult,
            create_partial_streamer,
        )
        
        print("\n[1/4] Creating partial streamer...")
        streamer = create_partial_streamer(
            backend_type="faster-whisper",
            model_size="tiny",  # Use tiny for faster testing
        )
        print("  [OK] Partial streamer created")
        
        print("\n[2/4] Testing callbacks...")
        partial_results = []
        final_results = []
        
        def on_partial(result: PartialResult):
            partial_results.append(result)
            print(f"  [PARTIAL] {result.text[:50]}...")
        
        def on_final(result: PartialResult):
            final_results.append(result)
            print(f"  [FINAL] {result.text}")
        
        streamer.set_callbacks(
            on_partial_result=on_partial,
            on_final_result=on_final,
        )
        print("  [OK] Callbacks set")
        
        print("\n[3/4] Testing streaming (mock audio)...")
        streamer.start_streaming()
        
        # Generate mock audio (silence + speech-like pattern)
        sample_rate = 16000
        duration = 2.0
        samples = int(sample_rate * duration)
        mock_audio = np.random.randn(samples).astype(np.float32) * 0.1
        
        streamer.add_audio_chunk(mock_audio)
        time.sleep(1.0)  # Wait for processing
        
        print("  [OK] Audio processed")
        
        print("\n[4/4] Testing stop streaming...")
        final_result = streamer.stop_streaming(finalize=True)
        print(f"  [OK] Streaming stopped (final_result={final_result is not None})")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S14-02: Partial Results - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_barge_in():
    """Test S14-03: Barge-In Detection."""
    print("\n" + "=" * 60)
    print("TEST S14-03: Barge-In (Interrupt TTS)")
    print("=" * 60)
    
    try:
        from core.audio.barge_in import BargeInDetector, create_barge_in_detector
        
        print("\n[1/3] Creating barge-in detector...")
        detector = create_barge_in_detector(sensitivity=0.3)
        print("  [OK] Barge-in detector created")
        
        print("\n[2/3] Testing callbacks...")
        barge_in_triggered = False
        speech_start_triggered = False
        
        def on_barge_in():
            nonlocal barge_in_triggered
            barge_in_triggered = True
            print("  [Barge-In] Detected!")
        
        def on_speech_start():
            nonlocal speech_start_triggered
            speech_start_triggered = True
            print("  [Speech Start] Detected!")
        
        detector.set_callbacks(
            on_barge_in=on_barge_in,
            on_speech_start=on_speech_start,
        )
        print("  [OK] Callbacks set")
        
        print("\n[3/3] Testing monitoring (mock audio)...")
        # Mock audio callback (simulating speech)
        def audio_callback():
            # Return speech-like audio
            samples = int(16000 * 0.1)  # 100ms chunks
            return np.random.randn(samples).astype(np.float32) * 0.3
        
        detector.start_monitoring(audio_callback)
        time.sleep(0.5)  # Let it detect
        detector.stop_monitoring()
        
        print(f"  [OK] Monitoring test complete")
        print(f"    Barge-in triggered: {barge_in_triggered}")
        print(f"    Speech start triggered: {speech_start_triggered}")
        
        stats = detector.get_stats()
        print(f"  Stats: {stats}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] S14-03: Barge-In - PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Sprint 14 tests."""
    print("\n" + "=" * 60)
    print("SPRINT 14: SPEECH EXCELLENCE - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test S14-01
    results.append(("S14-01: VAD Profiles", test_vad_profiles()))
    
    # Test S14-02
    results.append(("S14-02: Partial Results", test_partial_results()))
    
    # Test S14-03
    results.append(("S14-03: Barge-In", test_barge_in()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL SPRINT 14 TESTS PASSED!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("[WARNING] SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

