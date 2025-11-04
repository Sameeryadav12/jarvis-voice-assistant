# Jarvis Testing Guide

## Quick Testing Checklist

Let's test Jarvis step by step to ensure everything works!

## Step 1: Environment Setup ✅

### Activate Virtual Environment

**Windows**:
```powershell
cd D:\Projects\Jarvis
.\venv\Scripts\Activate.ps1
```

**Linux/macOS**:
```bash
cd ~/Projects/Jarvis
source venv/bin/activate
```

### Verify Installation

```bash
# Check Python
python --version
# Should show: Python 3.10+

# Check installed packages
pip list | grep -E "spacy|numpy|sounddevice|loguru|psutil"
```

---

## Step 2: Test Audio Capture 🎤

### List Audio Devices

```bash
python tests/test_audio_capture.py --mode list
```

**Expected**: List of your audio devices with input/output channels

### VU Meter Test (10 seconds)

```bash
python tests/test_audio_capture.py --mode vu --duration 10
```

**Expected**: 
- A meter showing audio levels as you speak
- Bars moving when you talk
- Press Ctrl+C to stop early

**What to check**:
- ✅ Meter responds to sound
- ✅ No errors about devices
- ✅ Clean exit

---

## Step 3: Test NLU (No API Keys Required!) 🧠

### Run Comprehensive NLU Tests

```bash
python tests/test_nlu.py
```

**Expected Output**:
```
Testing Intent Classification
✅ 'turn up the volume' → volume_up
✅ 'set volume to 50' → volume_set
✅ 'what time is it' → get_time
✅ 'check battery' → get_battery
...
Accuracy: 35/40 (87.5%)

Testing Entity Extraction
✅ 'set volume to 50' → percentage
✅ 'remind me in 5 minutes' → duration
✅ 'meeting tomorrow at 3pm' → date, time
...

Testing Complex Commands
📝 'remind me to call john tomorrow at 3pm'
   Intent: create_reminder
   Entities:
     - date: 2024-10-27
     - time: {'hour': 15, 'minute': 0}
```

**What to check**:
- ✅ Accuracy > 80%
- ✅ Entity extraction working
- ✅ No import errors

**If it fails with spaCy error**:
```bash
python -m spacy download en_core_web_sm
```

---

## Step 4: Test Console Mode (No API Keys!) 💬

### Basic Console Test

```bash
python jarvis.py --console
```

**Try these commands**:
```
You: help
Expected: Shows list of available commands

You: what time is it
Expected: "The time is [current time]"

You: what's the date
Expected: "Today is [current date]"

You: check battery
Expected: Battery info (or "No battery detected" on desktop)

You: system info
Expected: CPU, memory, OS information

You: set volume to 50
Expected: "Volume set to 50%" (or error if C++ module not built)

You: turn up the volume
Expected: "Volume increased to X%" (or error if C++ module not built)

You: thank you
Expected: "You're welcome!"

You: quit
Expected: Exits gracefully
```

**What to check**:
- ✅ All information commands work
- ✅ Responses are natural
- ✅ Clean exits
- ⚠️ Volume commands may fail (C++ module not built yet - this is normal!)

---

## Step 5: Test with Debug Mode 🔍

### Run with Debug Logging

```bash
python jarvis.py --console --debug
```

**What you'll see**:
- Detailed intent classification
- Entity extraction details
- Confidence scores
- Skill execution flow

**Try a command and observe**:
```
You: set timer for 5 minutes

[DEBUG] Intent: set_timer (confidence: 0.85)
[DEBUG] Entities: [duration=300]
[INFO] Result: Timer set for 5 minutes
```

---

## Step 6: Test Individual Components 🔧

### Test Entity Extraction

Create a quick test file:

```bash
python -c "
from core.nlu.entity_extractor import EntityExtractor

extractor = EntityExtractor()

# Test time
result = extractor.extract_time('meeting at 3:30 PM')
print('Time:', result)

# Test date
result = extractor.extract_date('remind me tomorrow')
print('Date:', result)

# Test duration
result = extractor.extract_duration('timer for 5 minutes')
print('Duration:', result)

# Test all
result = extractor.extract_all('meeting tomorrow at 3pm')
print('All entities:', result)
"
```

---

## Step 7: Test Skills Individually 🎯

### Test Information Skills

```bash
python -c "
from core.skills.information import InformationSkills

skills = InformationSkills()

# Test time
result = skills.get_time()
print('Time:', result.message)

# Test date
result = skills.get_date()
print('Date:', result.message)

# Test system info
result = skills.get_system_info()
print('System:', result.message)

# Test battery
result = skills.get_battery()
print('Battery:', result.message)
"
```

---

## Known Issues & Expected Behavior ⚠️

### ✅ Working (No API Keys Needed)
- Audio capture
- NLU intent classification
- Entity extraction
- Information skills (time, date, system, battery)
- Console mode
- Help command

### ⚠️ May Fail (Expected)
- **Volume Control**: Requires C++ module (Sprint 3)
  - Error: `jarvis_native module not found`
  - This is NORMAL - we haven't built the C++ module yet
  
- **Window Focus**: Requires C++ module
  - Error: `Native window module not available`
  - This is NORMAL

### 🔑 Requires API Keys
- **Wake Word Detection**: Needs Picovoice key
- **Voice Mode**: Needs Picovoice + Whisper/OpenAI
- **TTS**: Needs Piper models or Edge TTS access
- **Calendar**: Needs Google Calendar credentials

---

## Expected Test Results Summary 📊

| Test | Should Pass | Notes |
|------|-------------|-------|
| Audio Capture | ✅ YES | No dependencies |
| VU Meter | ✅ YES | Should show levels |
| NLU Tests | ✅ YES | 80%+ accuracy |
| Console Mode | ✅ YES | Info commands work |
| Entity Extraction | ✅ YES | All types working |
| Volume Control | ⚠️ May fail | C++ module not built |
| Window Focus | ⚠️ May fail | C++ module not built |
| Voice Mode | ⚠️ Needs keys | Requires Picovoice |

---

## Troubleshooting 🔧

### Issue: "No module named 'spacy'"
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Issue: "No module named 'psutil'"
```bash
pip install psutil
```

### Issue: "No module named 'sounddevice'"
```bash
pip install sounddevice
```

### Issue: Audio device errors
```bash
# List devices to see what's available
python tests/test_audio_capture.py --mode list
```

### Issue: "jarvis_native not found" (Volume/Window commands)
**This is expected!** The C++ module hasn't been built yet. This will be fixed in Sprint 3.

For now, these commands will show:
```
Result: Native audio module not available
```

---

## What Should Work vs. What Needs Setup 📝

### ✅ Works Right Now (Test These!)
1. Audio capture and VU meter
2. NLU intent classification (40+ intents)
3. Entity extraction (time, date, duration, etc.)
4. Console mode with text commands
5. Information skills:
   - What time is it?
   - What's the date?
   - Check battery
   - System info
   - Help
6. Debug mode

### 🔑 Needs API Keys (Optional)
1. Wake word detection → Get Picovoice key
2. Voice mode → Picovoice + Whisper models
3. Cloud STT → OpenAI API key

### 🔨 Needs Building (Sprint 3)
1. Volume control → Build C++ module
2. Window focus → Build C++ module

---

## Quick Test Command Summary 🚀

```bash
# 1. Audio test (10 seconds)
python tests/test_audio_capture.py --mode vu --duration 10

# 2. NLU test (comprehensive)
python tests/test_nlu.py

# 3. Console mode (interactive)
python jarvis.py --console

# 4. Console with debug
python jarvis.py --console --debug
```

---

## Next Steps After Testing ✨

Once tests pass:

### If Everything Works:
1. ✅ Continue to Sprint 3 (Build C++ module)
2. ✅ Get API keys for voice mode
3. ✅ Test full voice pipeline

### If Issues Found:
1. Check error messages
2. Verify dependencies installed
3. Review logs with --debug
4. Ask for help!

---

## Success Criteria ✅

You're ready to continue if:
- ✅ Audio capture works (VU meter shows levels)
- ✅ NLU tests pass with 80%+ accuracy
- ✅ Console mode responds to commands
- ✅ Information commands work (time, date, etc.)
- ⚠️ Volume commands show "module not available" (expected!)

---

**Ready to test?** Start with Step 1 and work through each test! 🚀





