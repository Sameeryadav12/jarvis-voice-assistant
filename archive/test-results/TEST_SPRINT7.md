# Testing Sprint 7 Features

## 🧪 Test Guide for Sprint 7 Components

This guide will help you test the new VAD and STT features.

---

## Prerequisites

### 1. Install Dependencies

Open PowerShell and activate your virtual environment:

```powershell
cd D:\Projects\Jarvis
.\venv\Scripts\Activate.ps1
```

Install the new dependencies:

```powershell
pip install silero-vad faster-whisper
```

**Note**: This will install PyTorch and other dependencies, which may take a few minutes.

---

## Test 1: Silero VAD

### What to Test
- Speech detection accuracy
- Latency (should be <30ms)
- False positive rate

### How to Run

```powershell
python core/audio/vad.py
```

### What to Expect
1. Console shows: "Loading Silero VAD model..."
2. Console shows: "Testing Silero VAD..."
3. Console prompts: "Speak now... (Ctrl+C to stop)"
4. When you speak, you should see:
   - `[VAD] Speech started` when you start talking
   - `[VAD] Speech stopped` when you stop

### Success Criteria
- ✅ Speech start detected quickly (<1 second delay)
- ✅ Speech stop detected after silence
- ✅ No false positives when not speaking

### Troubleshooting
- If you see "VAD not available", run `pip install silero-vad`
- If detection is too sensitive, edit `core/audio/vad.py` and increase threshold to 0.7

---

## Test 2: Faster Whisper STT

### What to Test
- Transcription accuracy
- Speed (should be 2-4× faster than standard Whisper)
- Model selection

### How to Run

```powershell
python core/audio/stt_faster_whisper.py
```

### What to Expect
1. Console shows: "Loading faster-whisper model..."
2. Shows available models list
3. Shows model info
4. Records 5 seconds of audio
5. Prints transcription and timing

### Example Output

```
Available models:
  tiny: {...}
  base: {...}
  small: {...}

Using model: {...}

Recording 5 seconds of audio...

Transcribing...
Transcribed in 0.85s:
'the quick brown fox jumps over the lazy dog'
```

### Success Criteria
- ✅ Transcription completes in <1 second (tiny model)
- ✅ Text is accurate
- ✅ No crashes or errors

### Troubleshooting
- First run will download the model (~200MB), be patient
- If you see "STT not available", run `pip install faster-whisper`
- For faster speed, edit the file and change `model_size="tiny"` to `model_size="base"`

---

## Test 3: STT Backend Manager

### What to Test
- Backend switching
- Factory function
- Manager functionality

### How to Run

```powershell
python core/audio/stt_backend.py
```

### What to Expect
1. Creates STT backend manager
2. Lists available backends
3. Records 5 seconds
4. Transcribes using current backend

### Example Output

```
Available backends: ['faster_whisper']
Manager: STTBackendManager(backend=faster_whisper)

Recording 5 seconds of audio...

Transcribing...
Transcribed in 0.82s:
'set a timer for five minutes'
```

### Success Criteria
- ✅ Manager initializes without errors
- ✅ Backend type is shown correctly
- ✅ Transcription works

---

## Test 4: VAD-Gated Audio Buffer

### What to Test
- Speech detection with buffering
- Pre/post-speech buffering
- Speech complete callbacks

### How to Run

```powershell
python core/audio/audio_buffer.py
```

### What to Expect
1. Creates VAD and buffer
2. Prompts: "Recording with VAD gating... (speak and then wait)"
3. When you speak:
   - Speech is detected
   - Audio is buffered
   - When you stop, callback triggers
4. Shows buffer statistics

### Example Output

```
[Callback] Speech received: 2.34s, 37440 samples

Buffer statistics:
  buffer_size: 37440
  buffer_duration_ms: 2340
  is_full: False
  is_recording: False
  speech_detected: True
  samples_added: 37440
  samples_skipped: 150600
  skip_ratio: 0.80
```

### Success Criteria
- ✅ Speech detected accurately
- ✅ Buffer captures complete speech
- ✅ Skips most silence (>50% skip ratio)
- ✅ Callback triggers after speech ends

### Troubleshooting
- If no speech detected, speak louder
- If callback doesn't trigger, wait 2-3 seconds after stopping speech
- Adjust VAD threshold if needed

---

## Test 5: Combined VAD + STT

### What to Test
- End-to-end speech detection and transcription
- Latency from speech start to transcript
- Complete pipeline

### Create Test Script

Create a file `test_vad_stt.py`:

```python
import sounddevice as sd
import time
from core.audio import create_vad, create_stt_backend_manager

print("Initializing VAD and STT...")
vad = create_vad(threshold=0.5)
stt = create_stt_backend_manager(
    backend_type="faster_whisper",
    faster_whisper={"model_size": "tiny"}
)

print("Recording 10 seconds...")
sample_rate = 16000
duration = 10
audio_data = sd.rec(
    int(sample_rate * duration),
    samplerate=sample_rate,
    channels=1,
    dtype='float32'
)
sd.wait()

print("Processing...")
start_time = time.time()
transcript = stt.transcribe(audio_data[:, 0], sample_rate)
elapsed = time.time() - start_time

print(f"\nTranscribed in {elapsed:.2f}s:")
print(f"'{transcript}'")
```

### Run Test

```powershell
python test_vad_stt.py
```

### Success Criteria
- ✅ Complete pipeline works (audio → transcript)
- ✅ Latency <1 second for short commands
- ✅ Accurate transcription

---

## Summary of Tests

| Test | Component | Command | Expected Result |
|------|-----------|---------|-----------------|
| 1 | VAD | `python core/audio/vad.py` | Speech detection |
| 2 | Faster-Whisper | `python core/audio/stt_faster_whisper.py` | Fast transcription |
| 3 | Backend Manager | `python core/audio/stt_backend.py` | Backend switching |
| 4 | Audio Buffer | `python core/audio/audio_buffer.py` | Speech buffering |
| 5 | Combined | `python test_vad_stt.py` | End-to-end |

---

## Performance Benchmarks

Run these tests to verify performance:

### Expected Latency

| Scenario | Target | Acceptable |
|----------|--------|------------|
| VAD Detection | <50ms | <100ms |
| STT (tiny) | <200ms | <500ms |
| STT (base) | <400ms | <800ms |
| End-to-End | <600ms | <1000ms |

### Expected CPU Usage

| Component | Target | Maximum |
|-----------|--------|---------|
| VAD | 2-5% | 10% |
| STT (tiny) | 20-40% | 60% |
| STT (base) | 40-60% | 80% |
| Overall | <50% | 70% |

---

## Quick Test Command

To run all tests at once:

```powershell
# Install dependencies
pip install silero-vad faster-whisper

# Test VAD
python core/audio/vad.py

# Test STT
python core/audio/stt_faster_whisper.py

# Test Buffer
python core/audio/audio_buffer.py
```

Press Ctrl+C to stop each test when done.

---

## Need Help?

If something doesn't work:
1. Check error messages
2. Verify dependencies are installed: `pip list | findstr silero`
3. Check microphone permissions
4. Try speaking louder or closer to microphone
5. Review logs for errors



