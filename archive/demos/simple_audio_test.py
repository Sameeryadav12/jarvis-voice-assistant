#!/usr/bin/env python3
"""Simple audio test - just generate and play one speech file"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.tts.edge import EdgeTTS

def main():
    print("\n" + "="*60)
    print("  SIMPLE AUDIO TEST")
    print("="*60)
    print()
    
    # Initialize TTS
    print("1. Initializing TTS...")
    tts = EdgeTTS()
    print("   [OK] TTS initialized!\n")
    
    # Generate speech
    print("2. Generating speech...")
    text = "Hello! I am Jarvis. This is a simple audio test."
    audio_file = "simple_test.mp3"
    
    success = tts.save_to_file(text, audio_file)
    
    if success:
        print(f"   [OK] Saved to {audio_file}")
        print(f"   File size: {os.path.getsize(audio_file) if os.path.exists(audio_file) else 0} bytes\n")
        
        # Play audio
        print("3. Playing audio...")
        print("   (Listen for Jarvis speaking!)\n")
        
        # Use simple approach
        import subprocess
        try:
            subprocess.run(["start", audio_file], shell=True, check=True)
            print("   [OK] Audio file launched in default player!")
            print("   You should hear Jarvis speaking now!\n")
        except Exception as e:
            print(f"   [ERROR] Could not play audio: {e}")
            print(f"   Please manually open: {os.path.abspath(audio_file)}\n")
    else:
        print("   [ERROR] Failed to generate speech\n")
    
    print("="*60)
    print("Test complete!")
    print("="*60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()




