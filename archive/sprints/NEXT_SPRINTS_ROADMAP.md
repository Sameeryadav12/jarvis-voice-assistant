# Next Sprints Roadmap (13-16)
## Voice Assistant Excellence

---

## 🎯 Overview

This document outlines the implementation plan for Sprints 13-16 to create a production-grade voice assistant with professional UI, advanced speech capabilities, daily-use skills, and polished packaging.

---

## 📋 Sprint 13: UI Polish & Tray App

### Goals
- Production-ready UI with professional design
- System tray integration
- Keyboard accessibility
- Fluid animations

### Tasks

#### S13-01: Voice Orb Component
**File**: `apps/desktop_ui/components/VoiceOrb.qml`

**Features**:
- Circular orb with amplitude-based animations
- Pulse effect during listening
- Sweep animation while speaking
- Color transitions (idle → listening → speaking)
- Breathing animation (spring/easing)

**Specifications**:
- Size: 120px diameter
- Colors: #5B8CFF (active), #647089 (idle)
- Animation: 250ms easing, 200ms transition

---

#### S13-02: Transcript Ticker
**File**: `apps/desktop_ui/components/TranscriptTicker.qml`

**Features**:
- Live partial ASR results (italic gray)
- Committed text (white)
- Auto-scroll
- Smooth transitions

---

#### S13-03: Activity Cards
**File**: `apps/desktop_ui/components/ActivityCard.qml`

**Features**:
- Chronological timeline
- Icon + intent name + timestamp
- User command + Jarvis response
- Actions: Re-speak, Copy, Pin to Memory, Undo

---

#### S13-04: Command Palette (Ctrl+K)
**File**: `apps/desktop_ui/components/CommandPalette.qml`

**Features**:
- Fuzzy search over skills/commands
- Keyboard shortcuts
- Recent commands
- Quick actions

---

#### S13-05: System Tray Integration
**File**: `apps/desktop_ui/TrayIcon.py`

**Features**:
- Mini orb icon
- Right-click menu
- Quick access to voice
- Notification integration

---

#### S13-06: Design System Implementation
**File**: `apps/desktop_ui/Theme.qml`

**Colors**:
- Background: #0B0F1A
- Surface: #111827
- Primary: #5B8CFF
- Success: #31EE88
- Warning: #F59E0B
- Critical: #EF4444

**Typography**:
- Font: Segoe UI Variable (Windows native)
- Display: 28-32px
- Body: 14-16px
- Caption: 12px

---

## 📋 Sprint 14: Speech Excellence

### Goals
- Ultra-low latency speech pipeline
- VAD tuning
- Interrupt handling (barge-in)
- Partial result captions

### Tasks

#### S14-01: VAD Microphone Profile Detection
**File**: `core/audio/vad_profiles.py`

**Features**:
- Auto-detect microphone characteristics
- Tune VAD thresholds per device
- Noise level calibration
- Background noise cancellation

---

#### S14-02: Partial Result Captions
**File**: `core/audio/stt_partial.py`

**Features**:
- Stream partial transcription results
- Update UI in real-time
- Visual feedback for accuracy
- Cancel mid-stream

---

#### S14-03: Barge-In (Interrupt TTS)
**File**: `core/audio/barge_in.py`

**Features**:
- Detect voice during TTS playback
- Stop TTS and switch to listening
- Resume or cancel context
- Smooth transitions

---

## 📋 Sprint 15: Daily-Use Skills

### Goals
- Must-have productivity features
- Reliable system integration
- Web quick-actions

### Tasks

#### S15-01: Enhanced Calendar Integration
**File**: `core/skills/calendar_enhanced.py`

**Features**:
- Natural language event creation
- Conflict detection
- Recurring rules parser
- Meeting summaries
- Auto-join meetings

---

#### S15-02: Quick Dictation
**File**: `core/skills/dictation.py`

**Features**:
- Voice-to-text in any app
- Worksystem clipboard integration
- Punctuation control
- Format commands (bold, italic)

---

#### S15-03: System Snapshot
**File**: `core/skills/system_snapshot.py`

**Features**:
- Current system state summary
- Resource usage overview
- Network status
- Application state

---

#### S15-04: Web Quick-Actions
**File**: `core/skills/web_quick.py`

**Features**:
- "Open [website]"
- "Search for [query]"
- "Bookmark this page"
- "Share current page"

---

## 📋 Sprint 16: Packaging & Distribution

### Goals
- Professional installer
- First-run wizard
- Auto-updates
- Silent deployment options

### Tasks

#### S16-01: MSIX Package Creation
**File**: `packaging/jarvis_msix.wxs`

**Features**:
- Windows 10+ package
- Side-by-side installation
- Automatic updates via Windows Store or custom
- Dependency management

---

#### S16-02: Inno Setup Installer
**File**: `packaging/Jarvis.iss`

**Features**:
- Classic wizard interface
- VC++ runtime bundling
- Optional voice model downloads
- Uninstaller

---

#### S16-03: First-Run Wizard
**File**: `apps/wizard/first_run.py`

**Steps**:
1. Welcome screen
2. Audio device selection
3. Wake word calibration
4. STT/TTS selection
5. Privacy settings
6. Account linking (optional)
7. Quick tour

---

#### S16-04: Autostart & System Tray
**File**: `core/autostart.py`

**Features**:
- Windows startup integration
- System tray with mini-orb
- Muted until wake word
- Background operation

---

#### S16-05: Update Channel
**File**: `core/updater.py`

**Features**:
- Check for updates
- Silent background updates
- Release notes display
- Rollback on failure

---

## 🎨 UI Design Specifications

### Layout

**Home Screen**:
```
┌─────────────────────────────────────┐
│  [Voice Orb - 120px centered]      │
│  [Transcript Ticker - top-center]  │
│  [Quick Chips]                      │
│  [Status Pill - bottom-left]        │
└─────────────────────────────────────┘
```

**Activity Screen**:
```
┌─────────────────────────────────────┐
│  Timeline Cards (scrollable)        │
│  ┌─────────────────────────────┐   │
│  │ 🕒 Time | 2 min ago         │   │
│  │ "what time is it"           │   │
│  │ "It's 3:42 PM"              │   │
│  │ [Play] [Copy] [Pin] [Undo]  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🔧 Technical Stack

### Audio Pipeline
1. **Wake Word**: Porcupine (on-device)
2. **VAD**: Silero VAD (speech gating)
3. **STT**: faster-whisper (local) OR OpenAI Realtime (cloud)
4. **NLU**: spaCy + patterns
5. **TTS**: edge-tts (cloud) OR Piper (local)

### Windows Integration
- **Volume Control**: WASAPI IAudioEndpointVolume
- **Window Management**: Win32 API
- **Notifications**: Windows toast API

### UI Framework
- **PySide6**: Qt for Python
- **QML**: Declarative UI language
- **QML Shaders**: For orb animations

---

## 📚 Documentation Plan

### User Documentation
1. Installation guide
2. Quick start tutorial
3. Balance sheet
4. Troubleshooting

### Admin Documentation
1. Deployment guide
2. Performance tuning
3. Network requirements
4. Security considerations

### Developer Documentation
1. Architecture overview
2. Skill development guide
3. UI components reference
4. API documentation

---

## 🎯 Success Criteria

- ✅ Voice orb responds in <100ms
- ✅ Partial results display in real-time
- ✅ System tray works flawlessly
- ✅ All keyboard shortcuts functional
- ✅ Installer successful on clean Windows
- ✅ First-run wizard completes in <2min
- ✅ Latency <250ms (cloud), <600ms (local)

---

## 🚀 Implementation Order

1. **Sprint 13**: UI Foundation
2. **Sprint 14**: Speech Pipeline
3. **Sprint 15**: Skills & Features
4. **Sprint 16**: Polish & Ship

盈利能力!



