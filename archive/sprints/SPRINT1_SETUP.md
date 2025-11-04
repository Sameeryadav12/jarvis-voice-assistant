# Sprint 1 - Wake Word + STT Setup Guide

This guide will help you set up and test the wake word detection and speech-to-text features.

## Overview

Sprint 1 adds:
- ✅ Wake word detection ("Hey Jarvis")
- ✅ Offline STT (whisper.cpp)
- ✅ Cloud STT (OpenAI Realtime API)
- ✅ Complete audio pipeline integration
- ✅ Voice mode application

## Prerequisites

Make sure you've completed Sprint 0:
- ✅ Virtual environment activated
- ✅ Dependencies installed
- ✅ Basic audio capture tested

## Step 1: Get Picovoice Access Key

### Free Tier (Recommended for Testing)

1. Go to [console.picovoice.ai](https://console.picovoice.ai)
2. Sign up for a free account
3. Copy your Access Key
4. Edit `config/settings.yaml`:

```yaml
wake_word:
  enabled: true
  access_key: "YOUR_ACCESS_KEY_HERE"  # Paste your key
  keyword: "jarvis"
  sensitivity: 0.5  # 0.0 to 1.0
```

**Free Tier Limits**:
- Unlimited on-device processing
- No cloud dependency
- Perfect for development

## Step 2: Choose STT Mode

### Option A: Offline STT (Recommended for Privacy)

**Advantages**:
- No internet required
- Complete privacy
- No API costs
- Fast (base model: ~300ms latency)

**Setup**:

1. **Download Whisper Model**:

```bash
# Create models directory
mkdir -p models

# Download base.en model (good balance of speed/accuracy)
cd models
# Windows PowerShell:
Invoke-WebRequest -Uri "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" -OutFile "ggml-base.en.bin"

# Linux/macOS:
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

**Model Options**:
- `ggml-tiny.en.bin` - Fastest, lowest accuracy (~50MB)
- `ggml-base.en.bin` - Good balance (~150MB) ⭐ Recommended
- `ggml-small.en.bin` - Better accuracy (~500MB)
- `ggml-medium.en.bin` - High accuracy (~1.5GB)

2. **Build whisper.cpp** (Optional but recommended):

```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Build
# Windows (with Visual Studio):
cmake -B build
cmake --build build --config Release

# Linux/macOS:
make

# Binary will be at:
# Windows: build/bin/Release/main.exe
# Linux/macOS: main
```

3. **Configure settings.yaml**:

```yaml
stt:
  mode: "offline"
  
  offline:
    model_path: "models/ggml-base.en.bin"
    binary_path: "whisper-cpp/main"  # or whisper-cpp/build/bin/Release/main.exe on Windows
    language: "en"
    num_threads: 4  # Adjust based on CPU
```

### Option B: Cloud STT (Lowest Latency)

**Advantages**:
- Lowest latency (~200ms)
- Best accuracy
- Function calling support
- No model downloads

**Setup**:

1. **Get OpenAI API Key**:
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create an API key
   - Add billing info (pay-per-use)

2. **Configure settings.yaml**:

```yaml
stt:
  mode: "cloud"
  
  cloud:
    api_key: "YOUR_OPENAI_API_KEY"
    model: "gpt-4o-realtime-preview-2024-10-01"
    voice: "alloy"
    temperature: 0.8
```

**Pricing**: ~$0.06 per minute of audio (as of 2024)

## Step 3: Test Components

### Test 1: Wake Word Detection

```bash
# Activate environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Test wake word (30 seconds)
python tests/test_wake_word.py \
  --access-key YOUR_PICOVOICE_KEY \
  --keyword jarvis \
  --duration 30
```

**What to expect**:
- Console shows "Listening..."
- Say "Hey Jarvis" or just "Jarvis"
- You should see "🎤 WAKE WORD DETECTED!"
- Detection count shown at end

**Troubleshooting**:
- If no detection: Try increasing sensitivity in settings
- If too many false positives: Decrease sensitivity
- Default sensitivity: 0.5 (good starting point)

### Test 2: Offline STT

```bash
# Test offline STT (5 second recording)
python tests/test_stt.py \
  --mode offline \
  --model-path models/ggml-base.en.bin \
  --whisper-bin whisper-cpp/main \
  --duration 5
```

**What to expect**:
- Console shows "Recording... Speak now!"
- VU meter shows audio levels
- After 5 seconds, transcription appears
- Check transcript accuracy

**Troubleshooting**:
- "Model not found": Download model (see Step 2A)
- "Binary not found": Build whisper.cpp or use full path
- Poor transcription: Try larger model (small or medium)

### Test 3: Cloud STT

```bash
# Test cloud STT
python tests/test_stt.py \
  --mode cloud \
  --api-key YOUR_OPENAI_KEY
```

**What to expect**:
- Connects to OpenAI API
- Tests connection
- Shows success message

**Troubleshooting**:
- "Invalid API key": Check key in settings
- Connection timeout: Check internet/firewall

### Test 4: Complete Pipeline

```bash
# Test full pipeline (60 seconds)
python tests/test_pipeline.py \
  --stt-mode offline \
  --wake-word-key YOUR_PICOVOICE_KEY \
  --wake-word jarvis \
  --model-path models/ggml-base.en.bin \
  --whisper-bin whisper-cpp/main \
  --duration 60
```

**Flow**:
1. Pipeline starts listening
2. Say "Hey Jarvis"
3. Wake word detected
4. Say a command (e.g., "turn up the volume")
5. After silence, transcript appears
6. Pipeline returns to listening

**What to expect**:
- "👂 Listening for wake word..."
- "✅ Wake word detected!"
- "🗣️ Listening to your command..."
- "🎤 TRANSCRIPT: turn up the volume"

## Step 4: Run Voice Mode

Now you can run Jarvis in full voice mode!

```bash
python jarvis_voice.py
```

**Usage**:
1. Say "Hey Jarvis" (or your configured wake word)
2. Wait for confirmation beep/message
3. Speak your command
4. Jarvis will process and respond

**Example Commands**:
- "Hey Jarvis... turn up the volume"
- "Hey Jarvis... set volume to 50"
- "Hey Jarvis... mute the system"
- "Hey Jarvis... focus on Chrome"

## Configuration Options

### Wake Word Tuning

```yaml
wake_word:
  sensitivity: 0.5  # Adjust this
```

**Sensitivity Guide**:
- `0.0-0.3`: Very conservative (fewer false positives, might miss some)
- `0.4-0.6`: Balanced (recommended) ⭐
- `0.7-1.0`: Sensitive (catches everything, more false positives)

### STT Tuning (Offline)

```yaml
stt:
  offline:
    num_threads: 4  # More threads = faster, but more CPU
```

**Thread Guide**:
- 2 threads: Low-end CPUs
- 4 threads: Mid-range CPUs ⭐
- 8+ threads: High-end CPUs

### Audio Settings

```yaml
audio:
  sample_rate: 16000  # Don't change (required for Porcupine)
  chunk_duration_ms: 30  # Lower = more responsive, higher CPU
```

## Performance Tips

### For Lower Latency

1. Use cloud STT mode
2. Use smaller Whisper model (tiny or base)
3. Increase CPU threads for Whisper
4. Reduce audio chunk duration (20-30ms)

### For Better Accuracy

1. Use larger Whisper model (small or medium)
2. Increase wake word sensitivity
3. Use good quality microphone
4. Reduce background noise

### For Lower CPU Usage

1. Use tiny Whisper model
2. Reduce thread count
3. Increase chunk duration
4. Consider cloud STT

## Common Issues

### Issue: Wake word not detecting

**Solutions**:
- Check microphone permissions
- Increase sensitivity in config
- Say wake word clearly and slowly
- Check microphone is default device

### Issue: STT transcription poor

**Offline**:
- Try larger model (small or medium)
- Speak clearly and at normal pace
- Reduce background noise
- Check microphone quality

**Cloud**:
- Check internet connection
- Verify API key is valid
- Check API quota/billing

### Issue: High CPU usage

**Solutions**:
- Use smaller Whisper model
- Reduce thread count
- Use cloud STT
- Increase chunk duration

### Issue: High latency

**Solutions**:
- Use cloud STT
- Use smaller Whisper model
- Increase thread count
- Check CPU isn't throttling

## Testing Checklist

Before moving to Sprint 2, verify:

- [ ] Wake word detection working
- [ ] STT transcribing correctly (offline or cloud)
- [ ] Complete pipeline runs without errors
- [ ] Voice mode responds to commands
- [ ] Latency acceptable (<1 second end-to-end)
- [ ] CPU usage reasonable
- [ ] No audio glitches or dropouts

## What's Next?

With Sprint 1 complete, you have:
- ✅ Working wake word detection
- ✅ Speech-to-text (offline or cloud)
- ✅ Complete audio pipeline
- ✅ Voice mode application

**Sprint 2** will add:
- Enhanced NLU with more intents
- More skills (calendar, reminders, web)
- Better context handling
- Conversation history

## Resources

- **Picovoice Console**: https://console.picovoice.ai
- **Whisper Models**: https://huggingface.co/ggerganov/whisper.cpp
- **whisper.cpp**: https://github.com/ggerganov/whisper.cpp
- **OpenAI Realtime**: https://platform.openai.com/docs/guides/realtime

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review logs with `--debug` flag
3. Open an issue on GitHub
4. Check discussions for similar problems

---

**Congratulations on completing Sprint 1!** 🎉

Your voice assistant can now:
- Detect wake words
- Transcribe speech
- Process voice commands
- Respond with actions

Time to move on to Sprint 2! 🚀





