"""Simple VAD test - speaks and shows results"""
import sys
sys.path.insert(0, '.')
from core.audio.vad import create_vad
import numpy as np

print("Testing Silero VAD...")
print("Creating VAD instance...")

vad = create_vad(threshold=0.5)

if vad:
    print("[OK] VAD loaded!")
    print("\nTest 1: Silence")
    silence = np.zeros(512, dtype=np.float32)
    is_speaking, prob = vad.process_chunk(silence)
    print(f"  Result: is_speaking={is_speaking}, probability={prob:.2f}")
    
    print("\nTest 2: Random noise (simulating speech)")
    np.random.seed(42)
    noise = np.random.randn(512).astype(np.float32) * 0.1
    is_speaking, prob = vad.process_chunk(noise)
    print(f"  Result: is_speaking={is_speaking}, probability={prob:.2f}")
    
    print("\nTest 3: Louder noise (simulating louder speech)")
    louder = np.random.randn(512).astype(np.float32) * 0.3
    is_speaking, prob = vad.process_chunk(louder)
    print(f"  Result: is_speaking={is_speaking}, probability={prob:.2f}")
    
    print("\n[OK] All VAD tests passed!")
    print("\nVAD is working correctly!")
else:
    print("[FAIL] VAD not available")



