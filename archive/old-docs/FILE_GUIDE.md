# 📁 Jarvis File Organization Guide

Quick reference for what each file does.

---

## ⭐ PRODUCTION FILES (Use These!)

### Main Application:
| File | Purpose | Use |
|------|---------|-----|
| **jarvis_simple_working.py** | ⭐ Production UI | **Main app - double-click START_JARVIS.bat** |
| **simple_tts.py** | Text-to-speech module | Used by main UI |
| **START_JARVIS.bat** | Launch script | Double-click to start |
| **run_ui.bat** | Alternative launcher | Also starts main UI |

### Documentation:
| File | Purpose |
|------|---------|
| **README_NEW.md** | Main documentation |
| **QUICKSTART_NEW.md** | Quick start guide |
| **INSTALLATION_NEW.md** | Installation instructions |
| **PROJECT_STATUS.md** | Project status |
| **CONTRIBUTING_NEW.md** | Contribution guidelines |
| **FILE_GUIDE.md** | This file |

### Core System:
| Folder | Purpose |
|--------|---------|
| **core/audio/** | Voice I/O (STT, TTS, VAD, etc.) |
| **core/nlu/** | Natural language understanding |
| **core/skills/** | Command handlers (system, info, reminders) |
| **core/memory/** | Vector memory storage |
| **core/config/** | Configuration management |

---

## 🧪 UTILITY FILES

### Testing & Verification:
| File | Purpose |
|------|---------|
| **CHECK_EVERYTHING.py** | Verify all systems working |
| **test_simple.py** | Test basic functionality |
| **test_volume.py** | Test volume control |
| **test_memory.py** | Test memory system |
| **demo.py** | Feature demonstration |

### Configuration:
| File | Purpose |
|------|---------|
| **requirements.txt** | Python dependencies |
| **config/settings.yaml** | Main configuration |

---

## 🗂️ LEGACY/ALTERNATIVE FILES (Optional)

### Alternative UIs (Not Recommended for Production):
| File | Status | Notes |
|------|--------|-------|
| jarvis_modern.py | Working but complex | Has threading complexity |
| jarvis_ui_neo.py | Complex | Neo-futuristic design, many states |
| jarvis_ui_simple.py | Older version | Superseded by simple_working |
| jarvis_ui.py | Has issues | QML loading problems |
| jarvis_ui_*.py | Various versions | Development versions |

### Old Demo Files:
| File | Status |
|------|--------|
| demo_*.py | Legacy | Old demos, not needed |
| quick_demo.py | Working | Simple demo |
| QUICK_DEMO_VOICE.py | Legacy | Superseded |

### Development Documentation (Archive):
| File | Status |
|------|--------|
| ALL_*_COMPLETE.md | Archive | Development history |
| SPRINT*.md | Archive | Sprint documentation |
| FINAL_*.md | Archive | Old status reports |
| TEST_*.md | Archive | Old test reports |
| *_STATUS.md | Archive | Old status files |

---

## 📦 BUILD/DIST FOLDERS

### Generated Folders (Can Ignore):
| Folder | Purpose |
|--------|---------|
| **venv/** | Virtual environment (don't commit) |
| **build/** | Build artifacts |
| **dist/** | Distribution packages |
| **__pycache__/** | Python cache |
| **logs/** | Log files |
| **chroma_db/** | Vector database |
| **tts_cache/** | TTS audio cache |
| **demo_memory/** | Demo database |
| **test_*_db/** | Test databases |

**Add to .gitignore:**
```
venv/
__pycache__/
*.pyc
build/
dist/
logs/
chroma_db/
tts_cache/
*_db/
```

---

## 🎯 RECOMMENDED USAGE

### For End Users:
1. Read: **README_NEW.md**
2. Quick start: **QUICKSTART_NEW.md**
3. Run: **START_JARVIS.bat**
4. Use: **jarvis_simple_working.py**

### For Developers:
1. Install: **INSTALLATION_NEW.md**
2. Contribute: **CONTRIBUTING_NEW.md**
3. Status: **PROJECT_STATUS.md**
4. Test: Run test files

### For GitHub:
1. Main README: **README_NEW.md**
2. License: **LICENSE**
3. Contributing: **CONTRIBUTING_NEW.md**
4. Requirements: **requirements.txt**

---

## 🧹 Cleanup Recommendations

### Files to Archive:
Move to `archive/` folder:
- All SPRINT*.md files
- All FINAL_*.md files
- All *_COMPLETE.md files
- All TEST_*.md files
- Old demo files
- Development status files

### Files to Keep:
- Main app files
- New documentation
- Core modules
- Test utilities
- Configuration

### Files to Delete:
- Duplicate demos
- Temporary test files
- Old UI versions (after testing new one)

---

## 📋 Quick Reference

### To Run Jarvis:
```
START_JARVIS.bat
```

### To Test:
```
python CHECK_EVERYTHING.py
```

### To Develop:
```
Edit: core/nlu/intents.py (add commands)
Edit: core/skills/ (add handlers)
Test: python test_simple.py
```

---

## 🎉 Clean Project Structure

After cleanup, your project should look like:

```
Jarvis/
├── START_JARVIS.bat          ⭐ Main launcher
├── jarvis_simple_working.py  ⭐ Main UI
├── simple_tts.py             ⭐ TTS module
├── requirements.txt          ⭐ Dependencies
│
├── README_NEW.md             📚 Main docs
├── QUICKSTART_NEW.md         📚 Quick start
├── INSTALLATION_NEW.md       📚 Installation
├── CONTRIBUTING_NEW.md       📚 Contributing
├── PROJECT_STATUS.md         📚 Status
├── FILE_GUIDE.md             📚 This file
│
├── core/                     🔧 Core modules
│   ├── audio/
│   ├── nlu/
│   ├── skills/
│   ├── memory/
│   └── config/
│
├── CHECK_EVERYTHING.py       ✅ System check
├── test_simple.py            ✅ Tests
├── demo.py                   ✅ Demo
│
├── config/                   ⚙️ Configuration
├── venv/                     📦 Virtual env
└── archive/                  📦 Old files
```

**Clean, organized, professional!** ✨

---

**Use this guide to navigate the Jarvis project efficiently!** 🗺️

