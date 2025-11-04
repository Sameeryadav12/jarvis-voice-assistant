# Voice Activity Detection (VAD) Guide

## Overview

Silero VAD is integrated into Jarvis to detect when speech starts and stops. This provides:

- **Lower latency**: Only process speech frames, skip silence
- **Reduced CPU usage**: Don't process background noise
- **Better accuracy**: STT focuses on actual speech

---

## Features

- Real-time detection on audio stream
- Configurable thresholds
- Speech start/stop callbacks
- Automatic model loading
- CPU optimized (ONNX runtime)

---

## Usage

### Basic Usage

```python
from core.audio.vad import create_vad

# Create VAD instance
vad = create_vad(threshold=0.5)

# Process audio chunks
is_speaking, probability = vad.process_chunk(audio_chunk)
```

### With Callbacks

```python
def on_speech_start():
    print("User started speaking")
    # Start recording for STT

def on_speech_stop():
    print("User stopped speaking")
    # Stop recording and transcribe

vad = create_vad(threshold=0.5)
vad.set_callbacks(
    on_speech_start=on_speech_start,
    on_speech_stop=on_speech_stop
)

# Process audio stream
for audio_chunk in audio_stream:
    vad.process_chunk(audio_chunk)
```

---

## Configuration

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `threshold` | 0.5 | Detection threshold (0.0-1.0). Higher = more strict |
| `min_speech_duration_ms` | 250 | Minimum speech duration to trigger "start" |
| `max_speech_duration_s` | inf | Maximum speech duration before forcing stop |
| `min_silence_duration_ms` | 500 | Minimum silence to trigger "stop" |
| `speech_pad_ms` | 400 | Extra padding around speech segments |
| `sample_rate` | 16000 | Audio sample rate (Hz) |

### Tuning Guide

**More Sensitive (detect quieter speech)**:
```python
vad = create_vad(threshold=0.3)  # Lower threshold
```

**Less Sensitive (fewer false positives)**:
```python
vad = create_vad(threshold=0.7)  # Higher threshold
```

**Quick Response (shorter silence required)**:
```python
vad = create_vad(
    threshold=0.5,
    min_silence_duration_ms=200  # Shorter silence
)
```

**No Interruptions (longer silence required)**:
```python
vad = create_vad(
    threshold=0.5,
    min_silence_duration_ms=1000  # Longer silence
)
```

---

## Integration with Audio Pipeline

VAD is integrated into the audio pipeline to gate frames:

```python
from core.audio import AudioCapture, create_vad

# Create VAD
vad = create_vad(threshold=0.5)

# Create audio capture
capture = AudioCapture(sample_rate=16000)

def process_audio(audio_chunk):
    # Check if speech
    is_speaking, prob = vad.process_chunk(audio_chunk)
    
    if is_speaking:
        # Send to STT
        transcript = stt.transcribe(audio_chunk)
        return transcript
    else:
        # Skip silence
        return None

# Capture loop
for audio_chunk in capture.stream():
    result = process_audio(audio_chunk)
```

---

## Performance

| Metric | Value |
|--------|-------|
| Latency | ~10-30 ms per chunk |
| CPU Usage | ~2-5% on modern CPU |
| Memory | ~50 MB (ONNX model) |
| False Positive Rate | <2% (default settings) |

---

## Troubleshooting

### "VAD not available"

Install Silero VAD:
```bash
pip install silero-vad
```

### High False Positive Rate

Increase threshold:
```python
vad = create_vad(threshold=0.7)
```

### Missing Speech Endings

Decrease min_silence_duration_ms:
```python
vad = create_vad(min_silence_duration_ms=200)
```

### Slow Detection

Use ONNX runtime (faster on CPU):
```python
# Already enabled by default
model, _ = silero_vad.load_vad_model(
    torch.device('cpu'),
    use_onnx=True
)
```

---

## Testing

Run the test script:
```bash
python core/audio/vad.py
```

This will:
1. Load VAD model
2. Start microphone capture
3. Show speech start/stop events
4. Press Ctrl+C to stop

---

## Resources

- [Silero VAD GitHub](https://github.com/snakers4/silero-vad)
- [Model Documentation](https://github.com/snakers4/silero-vad#models)
- [Performance Benchmarks](https://github.com/snakers4/silero-vad#benchmarks)

