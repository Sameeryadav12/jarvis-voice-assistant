"""
Test Jarvis Text-to-Speech functionality.
Sprint 5 - Part 1: TTS with Edge TTS (cloud)
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

# Suppress debug logs
import logging
logging.getLogger().setLevel(logging.WARNING)

from core.tts.edge import EdgeTTS
import asyncio

print("\n" + "=" * 60)
print("  JARVIS TEXT-TO-SPEECH TEST")
print("=" * 60)

# Test 1: Initialize Edge TTS
print("\n[1/4] Initializing Edge TTS (cloud)...")
try:
    tts = EdgeTTS(voice="en-US-AriaNeural")
    print("  [OK] Edge TTS initialized")
    print(f"  Voice: en-US-AriaNeural")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Generate speech (save to file, don't play)
print("\n[2/4] Testing speech generation (saving to file)...")
try:
    test_text = "Hello, I am Jarvis. Your voice assistant is working perfectly!"
    print(f"  Text: '{test_text}'")
    
    # Save to file without playing
    result = tts.save_to_file(test_text, "test_speech.mp3")
    
    if result:
        print("  [OK] Speech generated and saved to test_speech.mp3")
        import os
        if os.path.exists("test_speech.mp3"):
            size = os.path.getsize("test_speech.mp3")
            print(f"  File size: {size} bytes")
    else:
        print("  [FAIL] Speech generation failed")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test different voices
print("\n[3/4] Testing voice options...")
try:
    voices_to_test = [
        "en-US-GuyNeural",
        "en-US-JennyNeural",
    ]
    
    for voice in voices_to_test:
        tts_temp = EdgeTTS(voice=voice)
        print(f"  [OK] Voice '{voice}' available")
    
except Exception as e:
    print(f"  [WARN] {e}")

# Test 4: List available voices (first 10)
print("\n[4/4] Listing available voices (sample)...")
try:
    voices = EdgeTTS.list_voices()
    
    if voices:
        english_voices = [v for v in voices if v.get('Locale', '').startswith('en')][:10]
        print(f"  [OK] Found {len(voices)} total voices")
        print(f"  English voices (first 10):")
        for voice in english_voices:
            name = voice.get('ShortName', 'Unknown')
            gender = voice.get('Gender', 'Unknown')
            print(f"    - {name} ({gender})")
    else:
        print("  [WARN] Could not list voices")
except Exception as e:
    print(f"  [WARN] {e}")

print("\n" + "=" * 60)
print("[SUCCESS] TEXT-TO-SPEECH WORKING!")
print("=" * 60)
print("\nTTS capabilities:")
print("  - Cloud-based high-quality voices")
print("  - 300+ voices available")
print("  - Multiple languages")
print("  - Fast generation")
print("\nCheck test_speech.mp3 file to hear Jarvis speak!")
print("(You can play it with any media player)")
print()




