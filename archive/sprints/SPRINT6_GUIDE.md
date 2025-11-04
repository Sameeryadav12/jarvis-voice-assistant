# Sprint 6 Guide - Polish & Packaging

## Overview

**Sprint 6** focuses on final polish, packaging, and creating an installer for distribution.

**Goals**:
- ✅ Settings/Config system (Done!)
- 🔄 Package with PyInstaller
- 🔄 Create Windows installer
- 🔄 Add first-run wizard
- 🔄 Final polish

---

## Step 1: Configuration System ✅

### What We Built
- `core/config/config_manager.py` - Configuration manager
- YAML-based configuration
- Automatic defaults
- Easy get/set API

### Features
```python
from core.config import get_config

config = get_config()

# Get settings
app_name = config.get('general.app_name')
voice = config.get('tts.edge.voice')

# Set settings
config.set('general.app_name', 'My Jarvis')
config.save()
```

### Test
```powershell
python test_config.py
```

**Status**: ✅ **COMPLETE!**

---

## Step 2: Package with PyInstaller (Next Project)

### Overview
Create standalone executable:
```powershell
pyinstaller --onefile jarvis.py
```

This creates:
- `dist/jarvis.exe` - Single executable file
- Includes all dependencies
- Works without Python installed

### Install PyInstaller
```powershell
pip install pyinstaller
```

### Create Spec File
Create `jarvis.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['jarvis.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/settings.yaml', 'config'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'edge_tts',
        'chromadb',
        'apscheduler',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='jarvis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='Jarvis.app',
    icon=None,
    bundle_identifier='com.jarvis.assistant',
)
```

### Build
```powershell
pyinstaller jarvis.spec
```

---

## Step 3: Create Windows Installer (Inno Setup)

### Install Inno Setup
Download: https://jrsoftware.org/isdl.php

### Create Installer Script
Create `setup.iss`:
```iss
[Setup]
AppName=Jarvis
AppVersion=0.1.0
DefaultDirName={pf}\Jarvis
DefaultGroupName=Jarvis
OutputDir=dist
OutputBaseFilename=Jarvis_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\jarvis.exe"; DestDir: "{app}"
Source: "config\settings.example.yaml"; DestDir: "{app}\config"
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\Jarvis"; Filename: "{app}\jarvis.exe"
Name: "{commondesktop}\Jarvis"; Filename: "{app}\jarvis.exe"
```

### Build Installer
```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

---

## Step 4: First-Run Wizard

### Create Wizard
```python
# core/wizard.py
def run_first_run_wizard():
    """Interactive setup wizard."""
    print("Welcome to Jarvis!")
    print("Let's set up your assistant...\n")
    
    # 1. Name
    name = input("What would you like to call me? [Jarvis]: ") or "Jarvis"
    
    # 2. Voice
    print("\nAvailable voices:")
    print("1. Aria (Female)")
    print("2. Guy (Male)")
    voice_choice = input("Choose voice [1]: ") or "1"
    voice = "en-US-AriaNeural" if voice_choice == "1" else "en-US-GuyNeural"
    
    # 3. Save
    config = get_config()
    config.set('general.app_name', name)
    config.set('tts.edge.voice', voice)
    config.save()
    
    print(f"\nGreat! I'm {name} and ready to help!")
```

---

## Summary

**Sprint 6 Progress**:
- ✅ Step 1: Configuration system - COMPLETE
- 🔄 Step 2: PyInstaller packaging - Next
- 🔄 Step 3: Windows installer - After Step 2
- 🔄 Step 4: First-run wizard - After Step 3

**Current Completion**: 1/4 steps (25%)

---

**Ready to continue with Step 2: PyInstaller packaging?** 🚀




