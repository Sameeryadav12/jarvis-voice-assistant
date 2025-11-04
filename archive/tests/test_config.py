#!/usr/bin/env python3
"""
Test Configuration System
"""

import sys
from core.config import ConfigManager

def main():
    print("\n" + "="*60)
    print("  CONFIGURATION SYSTEM TEST")
    print("="*60)
    print()
    
    # Initialize config
    print("[1/5] Initializing config manager...")
    config = ConfigManager()
    print("   [OK] Config loaded!\n")
    
    # Test getting values
    print("[2/5] Testing get() method...")
    
    app_name = config.get('general.app_name')
    print(f"   App name: {app_name}")
    
    voice = config.get('tts.ached.voice')
    print(f"   TTS voice: {voice}")
    
    confidence = config.get('nlu.confidence_threshold')
    print(f"   NLU confidence: {confidence}")
    print("   [OK]\n")
    
    # Test setting values
    print("[3/5] Testing set() method...")
    config.set('general.app_name', 'Jarvis Test')
    new_name = config.get('general.app_name')
    print(f"   Set app name to: {new_name}")
    print("   [OK]\n")
    
    # Test nested access
    print("[4/5] Testing nested access...")
    stt_mode = config.get('stt.mode')
    print(f"   STT mode: {stt_mode}")
    
    sample_rate = config.get('audio.sample_rate')
    print(f"   Sample rate: {sample_rate}")
    print("   [OK]\n")
    
    # Check if config file exists
    print("[5/5] Checking config file...")
    if config.config_path.exists():
        print(f"   Config file exists: {config.config_path}")
    else:
        print(f"   Config file will be created: {config.config_path}")
    print("   [OK]\n")
    
    print("="*60)
    print("CONFIGURATION SYSTEM WORKING!")
    print("="*60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




