# 🚀 Jarvis Quick Start Guide

Get up and running with Jarvis in 5 minutes!

---

## Step 1: Install (2 minutes)

### Option A: Use the Installer (Easiest)

1. Download `JarvisSetup_1.0.0.exe` from Releases
2. Double-click to run
3. Follow the wizard (click Next, Next, Install)
4. Done! Jarvis is installed.

### Option B: Run from Source

```bash
# 1. Clone
git clone https://github.com/jarvis-assistant/jarvis.git
cd jarvis

# 2. Setup virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Run
python jarvis_ui.py
```

---

## Step 2: First Run Setup (3 minutes)

When you launch Jarvis for the first time, you'll see a setup wizard:

### Page 1: Welcome
- Click **Next**

### Page 2: Audio Devices
- **Microphone**: Select your microphone from dropdown
- Click **Test Microphone** to verify it works
- **Speakers**: Select your speakers
- Click **Test Speakers** to hear a test sound
- Click **Next**

### Page 3: Wake Word
- Keep **"Enable wake word detection"** checked (recommended)
- Adjust sensitivity slider if needed (50% is usually good)
- Optional: Click **Calibrate** and say "Hey Jarvis" a few times
- Click **Next**

### Page 4: Voice Processing
- **Speech-to-Text**: Choose "Offline" (no internet needed) or "Cloud" (more accurate)
- **Text-to-Speech**: Choose "Offline" or "Cloud"
- If using cloud: Enter your OpenAI API key (optional)
- Click **Next**

### Page 5: Privacy
- Choose whether to send anonymous usage stats (optional)
- Keep **crash reports** enabled (helps fix bugs)
- Click **Next**

### Page 6: Integrations
- Optionally enable Google Calendar integration
- Click **Next**

### Page 7: Complete!
- Check **"Launch Jarvis now"**
- Click **Finish**

---

## Step 3: Try Your First Commands!

Jarvis is now running! You'll see the voice orb in the window.

### Wake Word Mode (Default)

Say **"Hey Jarvis"** followed by a command:

```
"Hey Jarvis, what time is it?"
"Hey Jarvis, set volume to 50 percent"
"Hey Jarvis, search for Python tutorials"
```

### Push-to-Talk Mode

Or click the microphone button and speak:

```
[Click mic] "What's the weather?"
[Click mic] "Open YouTube"
[Click mic] "Set a reminder for 5 minutes"
```

---

## 🎯 Try These Commands

### System Control
```
"Set volume to 70 percent"
"Increase volume"
"Mute"
"Unmute"
"Focus Chrome window"
```

### Information
```
"What time is it?"
"What's the date?"
"Tell me a joke"
```

### Reminders & Time
```
"Set a timer for 5 minutes"
"Remind me to call John in 30 minutes"
"What's on my calendar today?"
```

### Web & Search
```
"Search for best restaurants near me"
"Open YouTube"
"Search GitHub for AI projects"
```

### System Info
```
"Show system status"
"How much memory am I using?"
"What's my battery level?"
```

---

## 💡 Tips

1. **Speak Clearly**: Normal pace, clear enunciation
2. **Wait for the Orb**: The voice orb turns blue when listening
3. **Use the Command Palette**: Press **Ctrl+K** for quick actions
4. **Check Activity History**: See all your past commands in the UI
5. **Adjust Sensitivity**: If wake word is too sensitive/not sensitive enough, adjust in settings

---

## 🔧 Quick Settings

Click the settings icon (gear) or press **Ctrl+,** to adjust:

- **Audio Devices**: Change microphone/speakers
- **Wake Word Sensitivity**: Make it more/less responsive
- **Voice Options**: Switch between offline/cloud
- **Autostart**: Launch Jarvis on Windows startup
- **Offline Mode**: Disable all internet features

---

## 📊 Status Indicators

Watch the voice orb:
- **Gray**: Idle, waiting for wake word
- **Blue**: Listening to your command
- **Green**: Processing command
- **Yellow**: Speaking response
- **Red**: Error occurred

---

## ❓ Having Issues?

### "Microphone not detected"
→ Check Windows Sound Settings → Input Devices

### "Wake word not responding"
→ Increase sensitivity in Settings → Wake Word

### "Commands not understood"
→ Try cloud STT for better accuracy (Settings → Voice)

### Still stuck?
→ Check logs: `%USERPROFILE%\.jarvis\logs\jarvis.log`

---

## 🎓 Learn More

- **Full Documentation**: See `README.md`
- **All Commands**: Press **Ctrl+K** in Jarvis
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **Advanced Config**: See `docs/CONFIGURATION.md`

---

## ✅ You're All Set!

Jarvis is now ready to help you. Here's what you can do:

✓ Control your computer with voice  
✓ Set reminders and timers  
✓ Search the web hands-free  
✓ Manage your calendar  
✓ Monitor system resources  
✓ And much more!

**Enjoy your new AI assistant!** 🤖

---

*Need help? Open an issue on GitHub or check the documentation.*
