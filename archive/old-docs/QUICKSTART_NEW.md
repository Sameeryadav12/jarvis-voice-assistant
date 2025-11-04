# 🚀 Jarvis Quick Start Guide

Get up and running with Jarvis in 5 minutes!

---

## ⚡ Super Quick Start

### Option 1: Double-Click to Run

**Windows:**
1. Double-click `START_JARVIS.bat`
2. Wait for UI to load (10-15 seconds first time)
3. Type `what time is it` and press Enter
4. Done! 🎉

### Option 2: Command Line

```bash
# Activate virtual environment
venv\Scripts\activate

# Run Jarvis
python jarvis_simple_working.py
```

---

## 📝 Your First Commands

### Try These Immediately:

**Type these in the input field:**
```
what time is it
check battery
show system status
help
```

**Or use voice:**
1. Click "🎙️ Voice"
2. Say: "Tell me the time"
3. Wait 5 seconds
4. Listen to response! 🔊

---

## 🎙️ Voice Commands Guide

### How to Use Voice:

**Step 1:** Click the **"🎙️ Voice"** button  
**Step 2:** Speak your command clearly  
**Step 3:** Wait for auto-stop (5s) or click **"⏹️ Stop"**  
**Step 4:** Listen to Jarvis respond! 🔊

### Voice Command Examples:

**Time & Date:**
- "What time is it"
- "Tell me the time"
- "What's the date"
- "Give me the time"

**Battery:**
- "Check battery"
- "Battery status"
- "How's the battery"
- "Battery life"

**System:**
- "Show system status"
- "System info"
- "How's my system"

**Volume:**
- "Set volume to 50"
- "Turn up the volume"
- "Mute"

---

## 🎯 Quick Command Buttons

The UI has 3 quick buttons at the bottom:

- **⏰ Time** - Instant time query
- **🔋 Battery** - Quick battery check
- **💻 System** - System information

Just click any button for an instant response!

---

## 🔊 Audio Features

### What You'll Hear:

**Every response speaks out loud!**

Examples:
- Type: "what time is it" → Hear: "The time is 8:05 PM" 🔊
- Voice: "check battery" → Hear: "Battery is at 80 percent and charging" 🔊
- Button: Click ⏰ → Hear current time 🔊

### No Speech Detection:

If Jarvis doesn't hear you:
- Shows: "I didn't hear anything..."
- Speaks: "I'm sorry, I didn't hear anything. Please try again." 🔊

---

## 💡 Tips for Best Results

### For Voice Commands:
✅ Speak clearly at normal pace  
✅ Reduce background noise  
✅ Wait for "Listening..." status  
✅ Speak within first 3 seconds  
✅ Let it auto-stop or click Stop  

### For Better Recognition:
✅ Use natural variations (Jarvis knows many patterns!)  
✅ Examples work best: time, battery, system, volume  
✅ Check console logs if something doesn't work  

---

## 🎨 UI Overview

### Left Panel:
- **JARVIS** title (blue)
- **Status indicator** (color-coded)
- **Text input field**
- **Voice & Send buttons**
- **Quick command buttons** (⏰ 🔋 💻)

### Right Panel:
- **Conversation title**
- **Chat history** (scrollable)
- **Status footer**

### Color Codes:
- 🟢 Green = Ready
- 🔵 Cyan = Listening/Recording
- 🟡 Orange = Processing
- 🔵 Blue = Speaking

---

## 🔧 Common Issues

### "Voice input not available"
```bash
pip install sounddevice numpy
pip install faster-whisper
```

### "TTS not working"
```bash
pip install edge-tts pygame
```

### "Module not found" errors
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 📚 More Help

- **Full README:** See `README.md`
- **Installation:** See installation steps above
- **Examples:** Check `demo.py` or `test_simple.py`
- **Logs:** Console shows detailed processing steps

---

## 🎮 Try These Now!

### Test 1: Simple Text
1. Type: `what time is it`
2. Press Enter
3. See and hear response!

### Test 2: Voice
1. Click "🎙️ Voice"
2. Say: "Check battery"
3. Wait 5 seconds
4. Hear response!

### Test 3: Quick Button
1. Click "⏰ Time"
2. Instant response!

---

**🎉 That's it! You're ready to use Jarvis!**

For more advanced features, see the full [README.md](README.md)

