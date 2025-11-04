"""
Quick test to hear Jarvis speak a short message.
Tests if audio playback works.
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from core.tts.edge import EdgeTTS

print("\n" + "=" * 60)
print("  JARVIS VOICE TEST - Listen for Audio!")
print("=" * 60)

print("\n[1/3] Initializing Edge TTS...")
tts = EdgeTTS(voice="en-US-AriaNeural")
print("  [OK] TTS ready\n")

print("[2/3] Generating speech...")
test_message = "Hello! I am Jarvis, your voice assistant. I am now fully functional!"
print(f"  Message: '{test_message}'")
print("  Generating audio...\n")

print("[3/3] Playing audio...")
print("  >>> LISTEN NOW <<<")
print("  (Make sure your speakers are on!)\n")

try:
    # This will play the audio
    tts.speak(test_message, play_audio=True)
    print("  [OK] Audio played successfully!")
except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Did you hear Jarvis speak? (Check your speakers)")
print("=" * 60)
print("\nIf you heard the voice:")
print("  ✅ TTS is working!")
print("  ✅ Ready to use jarvis_with_voice.py")
print("\nIf you didn't hear anything:")
print("  - Check speaker volume")
print("  - Check test_speech.mp3 was created")
print("  - Try playing test_speech.mp3 manually")
print()




