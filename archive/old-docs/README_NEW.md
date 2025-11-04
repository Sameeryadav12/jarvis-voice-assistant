# 🤖 JARVIS - Modern AI Voice Assistant

**A production-ready AI voice assistant for Windows with natural language understanding, voice I/O, and intelligent automation.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-blue)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

---

## ✨ Features

### 🎙️ Voice Processing
- **Voice Input** - 5-second voice recording with auto-stop
- **Speech-to-Text** - Faster Whisper (offline, fast, accurate)
- **Text-to-Speech** - Microsoft Edge TTS (natural neural voices)
- **Flexible Commands** - 5-6+ variations per command
- **Smart Apologies** - Responds when no speech detected

### 🧠 Natural Language Understanding
- **157 Intent Types** - Comprehensive command recognition
- **Flexible Patterns** - Multiple ways to say the same thing
- **High Accuracy** - 90%+ intent classification
- **Entity Extraction** - Understands dates, numbers, names

### 🛠️ Core Skills
- **System Control** - Volume, windows, power management
- **Information** - Time, date, battery, system stats
- **Reminders & Timers** - Never miss important tasks
- **Calendar Integration** - Google Calendar support
- **Memory System** - ChromaDB vector memory

### 🖥️ Modern User Interface
- **Clean Split Design** - Controls left, conversation right
- **Real-time Status** - Visual feedback for all states
- **Animated Orb** - Beautiful breathing animations
- **Dark Theme** - Professional blue color scheme
- **Responsive** - Smooth, no lag

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 or 11
- Python 3.11 or higher
- Microphone and speakers (for voice features)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

**2. Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**4. Run Jarvis:**
```bash
python jarvis_simple_working.py
```

---

## 💬 Usage

### Text Commands

Type any command in the input field and press Enter:

```
what time is it
check battery
set volume to 50
show system status
set timer for 5 minutes
help
```

### Voice Commands

1. Click **"🎙️ Voice"** button
2. Speak your command clearly
3. Wait 5 seconds (auto-stops) or click **"⏹️ Stop"**
4. Jarvis transcribes, processes, and responds with audio!

**Voice command examples:**
- "Tell me the time"
- "What's the current time"
- "Check the battery"
- "How's my battery"
- "Show system status"

### Quick Commands

Click the quick action buttons for instant commands:
- **⏰ Time** - Get current time
- **🔋 Battery** - Check battery status
- **💻 System** - View system information

---

## 🎯 Flexible Command Patterns

Jarvis understands multiple ways of saying the same thing:

### Time Command (12 variations):
✅ "what time is it"
✅ "tell me the time"
✅ "what's the time"
✅ "current time"
✅ "time please"
✅ "give me the time"
... and 6 more!

### Battery Command (11 variations):
✅ "check battery"
✅ "battery status"
✅ "how's the battery"
✅ "battery life"
✅ "show battery"
... and 6 more!

**Total: 50+ flexible pattern variations across all commands!**

---

## 🔊 Audio System

### Voice Input:
- **Engine:** Faster Whisper (Tiny model)
- **Quality:** High accuracy, fast processing
- **Duration:** 5-second recordings
- **Mode:** Offline (no internet required)

### Voice Output:
- **Engine:** Microsoft Edge TTS
- **Voice:** en-US-AriaNeural (clear female voice)
- **Quality:** Neural network TTS (natural sounding)
- **Speed:** Fast generation and playback

---

## 🏗️ Project Structure

```
Jarvis/
├── core/                          # Core functionality
│   ├── audio/                     # Voice I/O (STT, TTS, VAD)
│   ├── nlu/                       # Natural language understanding
│   ├── skills/                    # Skill modules (system, info, etc.)
│   ├── memory/                    # Vector memory (ChromaDB)
│   └── config/                    # Configuration management
├── apps/                          # UI applications
│   ├── desktop_ui/                # QML-based UI
│   └── wizard/                    # Setup wizard
├── jarvis_simple_working.py       # ⭐ Main production UI (USE THIS!)
├── simple_tts.py                  # Simple TTS implementation
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## ⚙️ Configuration

Jarvis works out of the box with sensible defaults. No configuration required!

Optional configuration in `config/settings.yaml`:

```yaml
audio:
  sample_rate: 16000
  
stt:
  model: "tiny"
  language: "en"

tts:
  voice: "en-US-AriaNeural"
```

---

## 🎨 UI Features

### Clean Modern Interface:
- **Split-panel design** - Controls on left, conversation on right
- **Dark theme** - Professional blue color palette
- **Animated orb** - Visual feedback for all states
- **Real-time status** - See exactly what Jarvis is doing

### State Indicators:
- 🟢 **Ready** - Waiting for command
- 🔵 **Listening** - Recording voice (5s countdown)
- 🟡 **Processing** - Analyzing command
- 🔵 **Speaking** - Delivering response

---

## 📊 Performance

| Component | Speed | Accuracy |
|-----------|-------|----------|
| Voice Recording | 5 seconds | N/A |
| Speech-to-Text | 1-2 seconds | 85-90% |
| Intent Classification | <50ms | 90%+ |
| Text-to-Speech | 1-2 seconds | Natural |
| Total Response Time | 2-5 seconds | N/A |

**System Requirements:**
- 4GB RAM minimum (8GB recommended)
- 500MB disk space (for models)
- Windows 10 (1809+) or Windows 11
- Microphone and speakers

---

## 🐛 Troubleshooting

### Voice recording doesn't work
- Check microphone permissions in Windows Settings
- Ensure microphone is not muted
- Try: `python -c "import sounddevice; print(sounddevice.query_devices())"`

### No audio output
- Check speaker volume
- Verify: `pip install pygame edge-tts`
- Test: `python simple_tts.py`

### Commands not recognized
- Speak clearly and at normal pace
- Try alternative phrasings (Jarvis knows 5-6 variations!)
- Check console logs for intent classification

### UI gets stuck on "Processing..."
- Check console output for errors
- Ensure all dependencies installed
- Restart the application

---

## 🔧 Development

### Running Tests:
```bash
python CHECK_EVERYTHING.py
python test_simple.py
python test_volume.py
```

### Key Files:
- `jarvis_simple_working.py` - Main production UI ⭐
- `simple_tts.py` - Text-to-speech module
- `core/nlu/intents.py` - Intent patterns (edit to add commands)
- `core/skills/` - Skill implementations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with amazing open-source technologies:
- **Faster Whisper** - Fast local speech recognition
- **Edge TTS** - High-quality text-to-speech
- **spaCy** - Natural language processing
- **PySide6/Qt6** - Modern UI framework
- **sounddevice** - Audio I/O

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/jarvis/issues)
- **Documentation:** See `docs/` folder
- **Examples:** Run `python demo.py`

---

## 🎯 Key Commands

### Information:
```
what time is it
what's the date
check battery
show system status
```

### System Control:
```
set volume to 50
turn up the volume
mute
```

### Reminders:
```
set timer for 5 minutes
list reminders
```

### Help:
```
help
what can you do
```

---

**Built with ❤️ for voice-controlled productivity**

*"Your personal AI assistant that actually works!"*

