# ✅ How to Run Jarvis (FIXED)

## ⚠️ IMPORTANT: Always Use venv Python!

### The Problem:
When you run `python core/audio/vad.py`, it uses your **system Python** which doesn't have numpy installed.

### The Solution:
Always use `venv\Scripts\python.exe` instead!

---

## 🚀 How to Run Commands

### Method 1: Use batch scripts (EASIEST) ✅
```bash
.\RUN_VAD.bat
.\run_tests.bat
.\test_vad.bat
```

### Method 2: Use venv Python directly ✅
```bash
venv\Scripts\python.exe core\audio\vad.py
venv\Scripts\python.exe test_sprint7_all.Markdown`
venv\Scripts\python.exe jarvis_simple.py
```

### Method 3: Activate venv first ✅
```bash
venv\Scripts\activate
python core\audio\vad.py
python jarvis_simple.py
```

---

## ❌ DON'T DO THIS
```bash
python core\audio\vad.py  # ❌ This will fail!
python test_sprint7_all.Markdown  # ❌ This will fail!
```

**Why?** This uses system Python without numpy, torch, etc.

---

## ✅ Summary

**Always use**: `venv\Scripts\python.exe`  
**Never use**: `python` (without venv)

That's it! Your code is perfect - just use the right Python! 🎯



