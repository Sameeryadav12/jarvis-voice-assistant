# 📦 Installation Guide

Complete installation instructions for Jarvis.

---

## 🖥️ System Requirements

### Minimum:
- **OS:** Windows 10 (1809+) or Windows 11
- **RAM:** 4GB
- **Disk:** 1GB free space
- **CPU:** Any modern processor
- **Audio:** Microphone and speakers

### Recommended:
- **RAM:** 8GB
- **Disk:** 2GB free space
- **CPU:** Multi-core processor
- **Internet:** For first-time setup (downloading models)

---

## 🔧 Prerequisites

### 1. Install Python

**Download Python 3.11 or higher:**
- Visit: https://www.python.org/downloads/
- Download Python 3.11+ for Windows
- **Important:** Check "Add Python to PATH" during installation

**Verify installation:**
```bash
python --version
# Should show: Python 3.11.x or higher
```

### 2. Git (Optional)

For cloning the repository:
- Download: https://git-scm.com/download/win
- Or download ZIP from GitHub

---

## 📥 Installation Steps

### Step 1: Get the Code

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to a folder
3. Open command prompt in that folder

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

This creates an isolated Python environment.

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**This installs:**
- PySide6 (UI framework)
- faster-whisper (Speech-to-Text)
- edge-tts (Text-to-Speech)
- pygame (Audio playback)
- spaCy (Natural Language Processing)
- sounddevice (Microphone input)
- And more...

### Step 5: Download Language Model

```bash
python -m spacy download en_core_web_sm
```

This downloads the English language model for NLU (~10MB).

### Step 6: Verify Installation

```bash
python CHECK_EVERYTHING.py
```

You should see:
```
[OK] All imports successful
[OK] Total intents: 157
[OK] NLU working
[OK] Bindings working
[SUCCESS] All checks passed!
```

---

## ▶️ Running Jarvis

### Option 1: Double-Click (Easiest)

Simply double-click:
```
START_JARVIS.bat
```

### Option 2: Command Line

```bash
# Make sure venv is activated
venv\Scripts\activate

# Run Jarvis
python jarvis_simple_working.py
```

### Option 3: From Python

```bash
python
>>> import subprocess
>>> subprocess.run(['python', 'jarvis_simple_working.py'])
```

---

## ✅ First Run Checklist

After launching, verify:

- [ ] UI window appears
- [ ] Left panel shows "JARVIS" in blue
- [ ] Status shows "● Ready" in green
- [ ] Input field is visible
- [ ] Buttons are present
- [ ] Right panel shows "Conversation"

**Test it:**
1. Type: `what time is it`
2. Press Enter
3. Should see response
4. Should HEAR response 🔊

---

## 🔄 Updating

To update Jarvis:

```bash
# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Re-download language model if needed
python -m spacy download en_core_web_sm
```

---

## 🗑️ Uninstallation

### Remove Jarvis:

```bash
# Deactivate virtual environment
deactivate

# Delete the entire folder
cd ..
rmdir /s /q jarvis
```

### Keep Settings:

Settings are stored in `config/settings.yaml`. Back up if needed.

---

## 🐛 Installation Troubleshooting

### "pip is not recognized"
- Python not added to PATH
- Reinstall Python and check "Add to PATH"

### "python is not recognized"
- Same as above
- Or use: `py` instead of `python`

### "ImportError: No module named..."
- Virtual environment not activated
- Run: `venv\Scripts\activate`
- Then: `pip install -r requirements.txt`

### "Failed to load model"
- Run: `python -m spacy download en_core_web_sm`
- Check internet connection

### "Audio device not found"
- Plug in microphone
- Check Windows sound settings
- Run: `python -c "import sounddevice; print(sounddevice.query_devices())"`

---

## 💻 Developer Installation

For development with additional tools:

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
python -m pytest tests/

# Format code
python -m black core/ apps/

# Type check
python -m mypy core/
```

---

## 🌐 Optional: Cloud Features

For cloud-based features (optional):

### Google Calendar Integration:
1. Get Google Calendar API credentials
2. Place in `config/google_credentials.json`

### OpenAI Integration (Optional):
1. Get OpenAI API key
2. Set environment variable: `OPENAI_API_KEY=your_key`

---

## ✨ Post-Installation

### What's Next?

1. **Read:** [QUICKSTART.md](QUICKSTART_NEW.md) for usage guide
2. **Try:** Voice commands - click "🎙️ Voice" and speak!
3. **Explore:** Check console logs to see what's happening
4. **Customize:** Edit `core/nlu/intents.py` to add commands

---

**🎉 Installation Complete! Enjoy your AI assistant!**

Run: `python jarvis_simple_working.py`

