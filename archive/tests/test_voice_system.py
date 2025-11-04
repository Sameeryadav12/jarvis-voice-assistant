"""
Test Voice System Components
Tests the secure voice input/output pipeline
"""

import sys
import io
from pathlib import Path

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.audio.voice_manager import (
    VoiceInputManager,
    SpeechToTextManager,
    TextToSpeechManager,
    VoiceManager
)


def test_voice_input():
    """Test voice input manager."""
    print("\n=== Testing Voice Input Manager ===")
    
    manager = VoiceInputManager()
    
    print(f"Voice input available: {manager.available}")
    
    if manager.available:
        print("✓ Voice input initialized successfully")
    else:
        print("✗ Voice input not available (sounddevice not installed)")
    
    return manager.available


def test_stt():
    """Test Speech-to-Text manager."""
    print("\n=== Testing Speech-to-Text (STT) ===")
    
    manager = SpeechToTextManager(model_size="base")
    
    print(f"STT available: {manager.available}")
    
    if manager.available:
        print("✓ STT initialized successfully (faster-whisper)")
        print(f"  Model: {manager.model_size}")
    else:
        print("✗ STT not available (faster-whisper not installed)")
    
    return manager.available


def test_tts():
    """Test Text-to-Speech manager."""
    print("\n=== Testing Text-to-Speech (TTS) ===")
    
    manager = TextToSpeechManager()
    
    print(f"TTS available: {manager.available}")
    
    if manager.available:
        print("✓ TTS initialized successfully (edge-tts)")
        print(f"  Voice: {manager.voice}")
        
        # Test speaking
        print("\n  Testing TTS output...")
        test_text = "Hello! I am Jarvis, your voice assistant."
        print(f"  Speaking: '{test_text}'")
        
        success = manager.speak(test_text)
        
        if success:
            print("✓ TTS test successful")
            import time
            time.sleep(3)  # Wait for speech to complete
        else:
            print("✗ TTS test failed")
        
        return success
    else:
        print("✗ TTS not available (edge-tts not installed)")
    
    return manager.available


def test_complete_voice_manager():
    """Test complete voice manager."""
    print("\n=== Testing Complete Voice Manager ===")
    
    manager = VoiceManager()
    
    print(f"\nVoice Manager Status:")
    print(f"  Input available: {manager.voice_input_available}")
    print(f"  STT available: {manager.stt_available}")
    print(f"  TTS available: {manager.tts_available}")
    print(f"  Fully operational: {manager.is_available()}")
    
    if manager.is_available():
        print("\n✓ Complete voice pipeline is ready!")
    else:
        print("\n⚠ Voice pipeline partially available")
        if not manager.voice_input_available:
            print("  Missing: sounddevice (pip install sounddevice)")
        if not manager.stt_available:
            print("  Missing: faster-whisper (pip install faster-whisper)")
        if not manager.tts_available:
            print("  Missing: edge-tts (pip install edge-tts)")
    
    return manager.is_available()


def main():
    """Run all voice system tests."""
    print("=" * 60)
    print("JARVIS VOICE SYSTEM TEST")
    print("=" * 60)
    
    results = {
        "Voice Input": test_voice_input(),
        "Speech-to-Text": test_stt(),
        "Text-to-Speech": test_tts(),
        "Complete Pipeline": test_complete_voice_manager()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Voice system is fully operational!")
    else:
        print("⚠ SOME TESTS FAILED - Check missing dependencies above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

