"""Quick VAD test"""
import sys
sys.path.insert(0, '.')
from core.audio.vad import create_vad

print("Testing VAD...")
try:
    vad = create_vad(threshold=0.5)
    if vad:
        print("[OK] VAD loaded successfully!")
        print("Testing with sample audio...")
        
        import numpy as np
        # Create test audio (silence)
        test_audio = np.zeros(512, dtype=np.float32)
        is_speaking, prob = vad.process_chunk(test_audio)
        print(f"[OK] Processed silence - Probability: {prob:.2f}")
        
        # Create test audio (pink noise to simulate speech)
        np.random.seed(42)
        test_speech = np.random.randn(512).astype(np.float32) * 0.1
        is_speaking, prob = vad.process_chunk(test_speech)
        print(f"[OK] Processed noise - Probability: {prob:.2f}")
        
        print("\n[OK] VAD test passed!")
    else:
        print("[FAIL] VAD not available")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

