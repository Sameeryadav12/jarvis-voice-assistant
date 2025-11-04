#!/usr/bin/env python
"""Test all imports."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Testing imports...")
print("=" * 60)

# Test imports one by one
tests = [
    ("numpy", "import numpy as np"),
    ("torch", "import torch"),
    ("faster_whisper", "from faster_whisper import WhisperModel"),
    ("silero_vad", "import silero_vad"),
]

for name, import_cmd in tests:
    try:
        exec(import_cmd)
        print(f"[OK] {name}")
    except ImportError as e:
        print(f"[FAIL] {name}: {e}")
        sys.exit(1)

print("=" * 60)
print("[SUCCESS] All imports working!")



