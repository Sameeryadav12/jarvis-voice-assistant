# Faster Whisper STT Guide

## Overview

faster-whisper is integrated into Jarvis as a fast local STT backend. It provides:

- **2-4× speedup** vs standard Whisper
- **8-bit quantization** for reduced memory
- **Auto device selection** (CPU/GPU)
- **Multiple model sizes** (tiny → large)

---

## Features

- Real-time transcription
- Auto device detection
- Quantized inference (int8)
- Streaming support
- Low memory footprint

---

## Usage

### Basic Usage

```python
from core.audio.stt_faster_whisper import create_faster_whisper

# Create STT instance (tiny model for speed)
stt = create_faster_whisper(model_size="tiny")

# Transcribe audio
transcript = stt.transcribe(audio_data, sample_rate=16000)
```

### Model Selection

```python
# Tiny: Fastest, good accuracy
stt = create_faster_whisper(model_size="tiny")

# Base: Balanced (recommended)
stt = create_faster_whisper(model_size="base")

# Small: Slower, best accuracy
stt = create_faster_whisper(model_size="small")

# Medium/Large: Very slow, excellent accuracy
stt = create_faster_whisper(model_size="medium")
```

### GPU Acceleration

```python
# Auto-detect GPU
stt = create_faster_whisper(
    model_size="base",
    device="auto"
)

# Force CPU
stt = create_faster_whisper(
    model_size="base",
    device="cpu"
)

# Force GPU
stt = create_faster_whisper(
    model_size="base",
    device="cuda"
)
```

### Quantization (Speed vs Accuracy)

```python
# int8: Fastest (2-4× speedup), lower accuracy
stt = create_faster_whisper(
    model_size="base",
    compute_type="int8"
)

# float16: Fast, higher accuracy (GPU only)
stt = create_faster_whisper(
    model_size="base",
    compute_type="float16"
)

# float32: Slowest, best accuracy
stt = create_faster_whisper(
    model_size="base",
    compute_type="float32"
)
```

---

## Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39M | Very fast | Good | Quick commands |
| base | 74M | Fast | Better | **Recommended** |
| small | 244M | Medium | Best | Long form |
| medium | 769M | Slow | Excellent | Quality priority |
| large | 1550M | Very slow | Best | Research |

---

## Configuration

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_size` | "base" | Model size (tiny/base/small/medium/large) |
| `device` | "auto" | Device (cpu/cuda/auto) |
| `compute_type` | "int8" | Compute type (int8/float16/float32) |
| `language` | "en" | Language code or None for auto-detect |
| `beam_size` | 5 | Beam search width |
| `best_of` | 5 | Number of candidates |
| `vad_filter` | True | Use internal VAD |

### Example Configurations

**Fastest (tiny, int8)**:
```python
stt = create_faster_whisper(
    model_size="tiny",
    compute_type="int8"
)
```

**Balanced (base, int8)**:
```python
stt = create_faster_whisper(
    model_size="base",
    compute_type="int8"
)
```

**Best Quality (small, float32)**:
```python
stt = create_faster_whisper(
    model_size="small",
    compute_type="float32"
)
```

**GPU Optimized (base, float16)**:
```python
stt = create_faster_whisper(
    model_size="base",
    device="cuda",
    compute_type="float16"
)
```

---

## Performance

### Benchmarks (10s audio, CPU)

| Model | int8 | float32 |
|-------|------|---------|
| tiny | ~200ms | ~400ms |
| base | ~300ms | ~800ms |
| small | ~600ms | ~1500ms |

### Benchmarks (10s audio, GPU)

| Model | int8 | float16 | float32 |
|-------|------|---------|---------|
| tiny | ~50ms | ~80ms | ~120ms |
| base | ~80ms | ~150ms | ~250ms |
| small | ~150ms | ~300ms | ~500ms |

---

## Integration

### With VAD

```python
from core.audio import create_vad, create_faster_whisper

# Create VAD and STT
vad = create_vad(threshold=0.5)
stt = create_faster_whisper(model_size="tiny")

def process_audio(audio_chunk):
    # Check if speech
    is_speaking, prob = vad.process_chunk(audio_chunk)
    
    if is_speaking:
        # Transcribe
        transcript = stt.transcribe_stream(audio_chunk)
        return transcript
    else:
        return None
```

### Streaming

```python
stt = create_faster_whisper(model_size="tiny")

for audio_chunk in audio_stream:
    transcript = stt.transcribe_stream(audio_chunk)
    if transcript:
        print(transcript)
```

---

## Troubleshooting

### "faster-whisper not available"

Install faster-whisper:
```bash
pip install faster-whisper
```

### Slow on CPU

Use int8 quantization:
```python
stt = create_faster_whisper(
    model_size="tiny",
    compute_type="int8"
)
```

### Out of memory

Use smaller model:
```python
stt = create_faster_whisper(model_size="tiny")
```

### Poor accuracy

Use larger model:
```python
stt = create_faster_whisper(model_size="small")
```

### GPU not detected

Check CUDA:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

---

## Comparison with whisper.cpp

| Feature | faster-whisper | whisper.cpp |
|---------|----------------|-------------|
| Speed | 2-4× faster | Baseline |
| Quantization | int8/float bundled | Manual setup |
| GPU | Native support | C++ bindings |
| Streaming | Limited | Yes |
| Setup | pip install | C++ compilation |

---

## Testing

Run the test script:
```bash
python core/audio/stt_faster_whisper.py
```

This will:
1. List available models
2. Load a model
-record 5 seconds of audio
3. Transcribe and show timing

---

## Resources

- [faster-whisper GitHub](https://github.com/guillaumekln/faster-whisper)
- [CTranslate2 Documentation](https://github.com/OpenNMT/CTranslate2)
- [Whisper Models](https://github.com/openai/whisper#available-models-and-languages)



