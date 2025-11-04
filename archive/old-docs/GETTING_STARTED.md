# Getting Started with Jarvis

This guide will help you get Jarvis up and running on your system.

## Prerequisites

### Required

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)

### Optional (for C++ hooks)

- **C++ Compiler**:
  - Windows: Visual Studio 2019+ with C++ tools
  - Linux: GCC 9+ or Clang 10+
  - macOS: Xcode Command Line Tools
- **CMake 3.20+** - [Download CMake](https://cmake.org/download/)

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd jarvis
```

### 2. Run Bootstrap Script

#### Windows (PowerShell)
```powershell
.\scripts\bootstrap_dev.ps1
```

#### Linux/macOS (Bash)
```bash
chmod +x scripts/bootstrap_dev.sh
./scripts/bootstrap_dev.sh
```

This script will:
- ✅ Create virtual environment
- ✅ Install Python dependencies
- ✅ Download spaCy language model
- ✅ Create necessary directories
- ✅ Set up configuration file

### 3. Configure Settings

Edit `config/settings.yaml` with your preferences:

```yaml
# Minimum required configuration
wake_word:
  access_key: "YOUR_PICOVOICE_KEY"  # Get from console.picovoice.ai

stt:
  mode: "offline"  # Start with offline mode

tts:
  mode: "piper"    # Start with offline TTS
```

### 4. Test Installation

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Test audio capture
python tests/test_audio_capture.py --mode vu --duration 5

# Test Jarvis in console mode
python jarvis.py --console
```

## Detailed Setup

### Step 1: Python Environment

#### Verify Python Version

```bash
python --version
# Should show Python 3.10 or higher
```

#### Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Download Language Models

#### spaCy Model (Required)

```bash
python -m spacy download en_core_web_sm
```

#### Whisper Model (Optional, for offline STT)

Download from [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp):

```bash
mkdir -p models
cd models
# Download base.en model (smaller, faster)
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

#### Piper TTS Model (Optional, for offline TTS)

Download from [Piper GitHub](https://github.com/rhasspy/piper/releases):

```bash
mkdir -p models/piper
cd models/piper
# Download your preferred voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
```

### Step 3: API Keys

#### Picovoice (Wake Word Detection)

1. Go to [console.picovoice.ai](https://console.picovoice.ai)
2. Sign up for free account
3. Get your Access Key
4. Add to `config/settings.yaml`:
   ```yaml
   wake_word:
     access_key: "YOUR_KEY_HERE"
   ```

#### OpenAI (Optional, for cloud STT/LLM)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create API key
3. Add to `config/settings.yaml`:
   ```yaml
   stt:
     cloud:
       api_key: "YOUR_KEY_HERE"
   ```

#### Google Calendar (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Google Calendar API
3. Create OAuth credentials
4. Download `credentials.json` to project root

### Step 4: Build C++ Hooks (Optional but Recommended)

C++ hooks provide system-level control (volume, window focus, etc.).

#### Install Build Tools

**Windows**:
1. Install [Visual Studio 2019+](https://visualstudio.microsoft.com/) with "Desktop development with C++"
2. Install [CMake](https://cmake.org/download/)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install build-essential cmake
```

**macOS**:
```bash
xcode-select --install
brew install cmake
```

#### Build

```bash
cd core/bindings/cpphooks

# Clone pybind11
git clone https://github.com/pybind/pybind11.git

# Create build directory
mkdir build
cd build

# Configure and build
cmake ..
cmake --build . --config Release

# Module will be placed in project root as jarvis_native.pyd/.so
```

#### Verify

```python
import jarvis_native
print(jarvis_native.__version__)
# Should print: 0.1.0
```

### Step 5: Test Components

#### Audio Capture

```bash
# VU meter demo (10 seconds)
python tests/test_audio_capture.py --mode vu --duration 10

# List audio devices
python tests/test_audio_capture.py --mode list

# Record and save
python tests/test_audio_capture.py --mode record --duration 5 --output test.wav
```

#### NLU (Intent Classification)

```python
from core.nlu.intents import IntentClassifier

classifier = IntentClassifier()
intent = classifier.classify("turn up the volume")
print(f"Intent: {intent.type.value}")  # Should be: volume_up
```

#### TTS

```python
from core.tts.edge import EdgeTTS

tts = EdgeTTS()
tts.speak("Hello, I am Jarvis")
```

#### C++ Hooks

```python
import jarvis_native

# Set volume to 50%
jarvis_native.set_master_volume(0.5)

# Get current volume
vol = jarvis_native.get_master_volume()
print(f"Volume: {vol * 100}%")

# Focus a window
jarvis_native.focus_window("Visual Studio")
```

### Step 6: Run Jarvis

#### Console Mode (Text Input)

```bash
python jarvis.py --console
```

This mode lets you type commands for testing:
```
You: turn up the volume
Result: Volume increased to 60%

You: remind me to call mom in 1 hour
Result: Reminder set for 3:00 PM

You: quit
```

#### Voice Mode (Coming Soon)

```bash
python jarvis.py --voice
```

This will enable:
- Wake word detection
- Voice input
- Speech output

## Common Issues

### Issue: Module 'sounddevice' not found

**Solution**:
```bash
pip install sounddevice
```

### Issue: spaCy model not found

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: C++ build fails on Windows

**Solution**:
- Ensure Visual Studio with C++ tools is installed
- Run from "x64 Native Tools Command Prompt for VS"
- Check CMake is in PATH

### Issue: Permission denied on Linux/macOS for audio

**Solution**:
```bash
# Add user to audio group (Linux)
sudo usermod -a -G audio $USER

# Restart session or run:
newgrp audio
```

### Issue: Import error for jarvis_native

**Solution**:
1. Ensure C++ build completed successfully
2. Check `jarvis_native.pyd` (Windows) or `jarvis_native.so` (Linux/macOS) exists in project root
3. Try running from project root directory

### Issue: Porcupine access key invalid

**Solution**:
1. Verify key is correct in `config/settings.yaml`
2. Check key hasn't expired at console.picovoice.ai
3. Ensure no extra whitespace in config file

## What's Next?

### Learn the Basics

- Read [README.md](../README.md) for project overview
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
- Check [CPP_HOOKS.md](CPP_HOOKS.md) for C++ development

### Customize Jarvis

- Edit `config/settings.yaml` for preferences
- Add custom intent patterns
- Create your own skills

### Contribute

- Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- Pick an issue from GitHub
- Submit a pull request

### Development Workflow

```bash
# Activate environment
source venv/bin/activate  # or venv\Scripts\Activate.ps1

# Run tests
pytest tests/

# Check code style
black core/ tests/
flake8 core/ tests/

# Run Jarvis
python jarvis.py --console --debug
```

## Configuration Options

### Audio Settings

```yaml
audio:
  sample_rate: 16000      # Hz
  channels: 1             # Mono
  chunk_duration_ms: 30   # Milliseconds
  input_device: null      # null = default
```

### STT Settings

```yaml
stt:
  mode: "offline"  # or "cloud"
  
  offline:
    model_path: "models/ggml-base.en.bin"
    num_threads: 4
  
  cloud:
    api_key: "YOUR_KEY"
    model: "gpt-4o-realtime-preview-2024-10-01"
```

### TTS Settings

```yaml
tts:
  mode: "piper"  # or "edge"
  
  piper:
    model_path: "models/piper/en_US-lessac-medium.onnx"
  
  edge:
    voice: "en-US-AriaNeural"
```

## Performance Tips

### For Lower Latency

1. Use offline STT (whisper.cpp) instead of cloud
2. Use smaller Whisper model (tiny or base)
3. Use Piper TTS instead of Edge
4. Increase CPU thread count for Whisper
5. Run on SSD for faster model loading

### For Better Accuracy

1. Use cloud STT (OpenAI Realtime)
2. Use larger Whisper model (medium or large)
3. Adjust wake word sensitivity
4. Use higher quality microphone
5. Reduce background noise

### For Lower Resource Usage

1. Use tiny Whisper model
2. Reduce audio buffer size
3. Disable unused skills
4. Disable memory/RAG if not needed
5. Use cloud services (offload processing)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/jarvis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/jarvis/discussions)
- **Documentation**: [docs/](.)

## License

MIT License - see [LICENSE](../LICENSE) for details

---

**Ready to build your voice assistant?** Start with console mode and gradually add features! 🚀





