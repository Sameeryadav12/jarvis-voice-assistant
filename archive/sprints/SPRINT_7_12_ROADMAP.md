# 🚀 Jarvis Advanced Roadmap - Sprints 7-12

## Overview

Building from the solid foundation of Sprints 0-6, these advanced sprints will transform Jarvis into a production-grade assistant.

---

## 📊 Current Status

**Completed**: Sprints 0-6 (100%)
- ✅ Core NLU with spaCy
- ✅ Basic skills (Information, System, Reminders)
- ✅ Windows integration
- ✅ PyInstaller packaging
- ✅ Desktop UI foundation

**Next**: Sprints 7-12 (Planned)

---

## 🎯 Sprint 7: Realtime Speech Polish

### Goals
- Near-instant response times
- Rock-solid wake word and VAD detection
- Support multiple STT backends

### Tasks

#### S7-01: Integrate Silero VAD
- **File**: `core/audio/vad.py`
- **Dependencies**: `silero-vad` (PyPI)
- **Acceptance**: <2% false start rate
- **Documentation**: VAD tuning guide

#### S7-02: Add faster-whisper Backend
- **File**: `core/stt/faster_whisper.py`
- **Dependencies**: `faster-whisper` (PyPI)
- **Features**:
  - Auto model selection (tiny/base/small)
  - 8-bit quantization
  - Device auto-select (CPU/GPU)
- **Acceptance**: 2-4× speedup vs whisper.cpp

#### S7-03: STT Backend Strategy
- **File**: `core/stt/backend.py`
- **Strategy Pattern**: Hot-swap backends without code changes
- **Backends**:
  - whisper.cpp (existing)
  - faster-whisper (new)
  - OpenAI Realtime (future)

#### S7-04: Audio Ring Buffer with VAD Gating
- **File**: `core/audio/buffer.py`
- **Feature**: Only send voiced frames to STT
- **Benefit**: Reduced latency, lower CPU usage

#### S7-05: Benchmark Suite
- **File**: `tests/benchmark_stt.py`
- **Metrics**: Latency, accuracy, resource usage
- **Documentation**: Performance report

### Acceptance Criteria
- ✅ <250 ms wake-to-transcript (cloud)
- ✅ <600 ms wake-to-transcript (local small model)
- ✅ No false positives >1/min
- ✅ Backend switching <100 ms

---

## 🎯 Sprint 8: Assistant-Grade NLU & Function Calling

### Goals
- Siri/Google Assistant-like "understand anything"
- Safe tool calling with validation

### Tasks

#### S8-01: Intent Packs (80+ Intents)
- **Files**: 
  - `core/nlu/intents/system.py`
  - `core/nlu/intents/communication.py`
  - `core/nlu/intents/calendar.py`
  - `core/nlu/intents/web.py`
  - `core/nlu/intents/notes.py`
- **Structure**: Intent families with patterns and entities

#### S8-02: Rasa-Style Pipeline Option
- **File**: `core/nlu/rasa_pipeline.py`
- **Dependencies**: `rasa` (PyPI)
- **Documentation**: Training data format (YAML)

#### S8-03: Function Calling Schemas
- **File**: `core/skills/schema.py`
- **Feature**: JSON schema for each skill
- **Validation**: Parameter type checking

#### S8-04: Function Calling Router
- **File**: `core/skills/function_caller.py`
- **Integration**: OpenAI Realtime function calling
- **Safety**: Confirm before execution

#### S8-05: Skill Registry
- **File**: `core/skills/registry.py`
- **Feature**: Dynamic skill discovery and registration

### Acceptance Criteria
- ✅ ≥90% intent precision on test set
- ✅ Safe parameter validation for all skills
- ✅ Rasa pipeline working end-to-end
- ✅ Function calling schemas for all skills

---

## 🎯 Sprint 9: UI v1 (Modern & Delightful)

### Goals
- First-party assistant feel
- 60 FPS animations
- Full accessibility

### Tasks

#### S9-01: PySide6/QML Setup
- **Files**:
  - `apps/ui/main.qml`
  - `apps/ui/components/`
- **Framework**: PySide6 with QML for animations

#### S9-02: Voice Orb Component
- **File**: `apps/ui/components/VoiceOrb.qml`
- **Features**:
  - Radial energy visualization
  - Amplitude feedback
  - Speaking state indicators
- **Pattern**: Canvas/QML shader

#### S9-03: Transcript Ticker
- **File**: `apps/ui/components/TranscriptTicker.qml`
- **Features**:
  - Live partial results (italic gray)
  - Committed text (white)
  - Auto-scroll

#### S9-04: Activity Cards
- **File**: `apps/ui/components/ActivityCard.qml`
- **Features**:
  - Chronological timeline
  - Command → Action → Result
  - Undo buttons

#### S9-05: Command Palette (Ctrl+K)
- **File**: `apps/ui/components/CommandPalette.qml`
- **Features**: Fuzzy search over skills/hotkeys

#### S9-06: Settings Panel
- **File**: `apps/ui/pages/Settings.qml`
- **Tabs**:
  - Audio (devices, input levels)
  - Speech (wake word, STT, VAD)
  - Skills (permissions)
  - Accounts (API keys)
  - Privacy (offline mode)
  - About

#### S9-07: System Tray Integration
- **File**: `apps/ui/TrayIcon.py`
- **Features**: Minimal overlay, quick access

#### S9-08: Themes & Accessibility
- **Features**:
  - Light/Dark themes
  - High contrast mode
  - Keyboard navigation
  - Captions toggle

### Acceptance Criteria
- ✅ 60 FPS steady animation
- ✅ DPI-aware rendering
- ✅ Full keyboard accessibility
- ✅ Tray mode working
- ✅ Themes switchable

---

## 🎯 Sprint 10: Pro-Level Skills

### Goals
- Out-of-the-box useful features
- 95% success rate across 30-task scenario

### Tasks

#### S10-01: Communication Skills
- **Files**:
  - `core/skills/email.py`
  - `core/skills/messages.py`
- **Features**:
  - Dictate email (Gmail)
  - Read new mail
  - Quick reply drafts

#### S10-02: Calendar Integration
- **File**: `core/skills/calendar.py`
- **Features**:
  - Natural language create/move meetings
  - Conflict detection
  - Recurring rules

#### S10-03: Tasks & Reminders
- **File**: `core/skills/tasks.py`
- **Features**:
  - Recurring rules (weekdays at 7am)
  - Snooze functionality
  - Follow-up chains

#### S10-04: Web Agent (Playwright)
- **File**: `core/skills/web_agent.py`
- **Dependencies**: `playwright` (PyPI)
- **Features**:
  - "Download my payslip"
  - "Check parcel status"
  - "Fill timesheet"
  - Confirmations for risky actions

#### S10-キャン
- **File**: `core/skills/system.py` (extend)
- **Features**:
  - Media controls
  - Wi-Fi status
  - Screen brightness (per-OS)
  - Screenshot & summarize

#### S10-06: Rollback & Confirmations
- **File**: `core/skills/safety.py`
- **Features**:
  - Rollback on failure
  - Confirmations for risky actions
  - Skill execution logs

### Acceptance Criteria
- ✅ 95% success across 30-task scenario
- ✅ Rollback working
- ✅ Confirmations shown for risky actions
- ✅ All skills logged

---

## 🎯 Sprint 11: Privacy, Security & Packaging

### Goals
- Production-ready trust
- Multi-platform distribution

### Tasks

#### S11-01: Permissions System
- **File**: `core/permissions.py`
- **Scopes**: system, filesystem, network, clipboard
- **Features**: Per-skill consent

#### S11-02: Secrets Vault
- **File**: `core/secrets.py`
- **Dependencies**: `keyring` (PyPI)
- **Features**: Encrypted API keys/tokens

#### S11-03: Offline Mode
- **File**: `core/config.py` (extend)
- **Features**:
  - Local STT/TTS only
  - Local embeddings
  - Network toggle

#### S11-اختبار
- **File**: `installers/`
- **Platforms**:
  - Windows (.exe installer)
  - macOS (.app bundle)
  - Linux (.AppImage)
- **Dependencies**: PyInstaller, Inno Setup, create-dmg

#### S11-05: First-Run Wizard
- **File**: `core/wizard.py` (enhance)
- **Features**:
  - Permissions setup
  - API key entry
  - Audio device selection

#### S11-06: Crash Reporter
- **File**: `core/reporter.py`
- **Features**: Auto report + manual "view logs"

### Acceptance Criteria
- ✅ All platforms packaged
- ✅ Signed binaries (Windows/macOS)
- ✅ First-run wizard complete
- ✅ Crash reporter working
- ✅ Secrets encrypted

---

## 🎯 Sprint 12: Performance, Observability & Docs

### Goals
- Measurable, tunable, transparent

### Tasks

#### S12-01: Metrics Overlay
- **File**: `apps/ui/components/MetricsOverlay.qml`
- **Metrics**: Pipeline timings (wake → STT → NLU → action → TTS)

#### S12-02: Profiling Tools
- **File**: `tools/profiler.py`
- **Features**: CPU/GPU traces for STT/TTS

#### S12-03: Auto Recommendations
- **File**: `core/recommendations.py`
- **Features**: Switch STT to tiny when CPU high

#### S12-04: User Documentation
- **File**: `docs/USER_GUIDE.md`
- **Sections**:
  - Installation
  - Configuration
  - Usage (commands)
  - Troubleshooting

#### S12-05: Admin Documentation
- **File**: `docs/ADMIN_GUIDE.md`
- **Sections**:
  - Deployment
  - Performance tuning
  - Custom skills

#### S12-06: Developer Documentation
- **File**: `docs/DEVELOPER_GUIDE.md`
- **Sections**:
  - Architecture
  - Writing skills
  - Contributing

### Acceptance Criteria
- ✅ Latency report page
- ✅ "Recommend settings" button working
- ✅ 100% docs for all features
- ✅ Profiling tools working

---

## 📚 Library Dependencies

```txt
# New dependencies for Sprints 7-12
silero-vad>=4.0.0          # VAD
faster-whisper>=1.0.0      # Fast STT
rasa>=3.6.0                # NLU pipeline (optional)
playwright>=1.40.0         # Web automation
keyring>=24.0.0            # Secrets vault
PySide6>=6.6.0             # UI framework (already have)
```

---

## 🎨 UI Design Spec

### Style
- **Primary**: Electric blue accent (#007ACC)
- **Secondary**: Mint/Teal success (#00C896)
- **Support**: Dark/Light themes

### Typography
- **Font**: Inter or SF Pro-like
- **Headings**: Large, friendly
- **Body**: Readable microcopy

### Motion
- Voice orb grows with amplitude
- Intent chips animate in
- Toasts slide from tray

### Components
1. **Voice Orb**: Canvas shader
2. **Transcript**: Live → committed
3. **Action Cards**: Icon, title, undo
4. **Command Palette**: Ctrl/Cmd+K
5. **Settings**: Tabbed interface

---

## 🏗️ Architecture Patterns

### Backend Strategy
```python
class STTBackend(ABC):
    @abstractmethod
    def transcribe(self, audio: bytes) -> str:
        pass

class WhisperBackend(STTBackend):
    def transcribe(self, audio: bytes) -> str:
        # Implementation
        pass

class FasterWhisperBackend(STTBackend):
    def transcribe(self, audio: bytes) -> str:
        # Implementation
        pass
```

### Function Calling Schema
```python
class SkillSchema(TypedDict):
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Any

def get_skill_schema(skill_name: str) -> SkillSchema:
    # Return validated schema
    pass
```

### Permissions Scoping
```python
class PermissionScope(Enum):
    SYSTEM = "system"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    CLIPBOARD = "clipboard"

def check_permission(skill: str, scope: PermissionScope) -> bool:
    # Check consent
    pass
```

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Wake → Transcript (cloud) | <250 ms | ~500 ms |
| Wake → Transcript (local) | <600 ms | ~1200 ms |
| Intent Precision | ≥90% | ~89.7% |
| UI FPS | 60 | N/A |
| False Positives | <1/min | ~2/min |

---

## 🎓 Next Steps

Start with **Sprint 7 Task S7-01**: Integrate Silero VAD

**Ready to begin?** Let's implement Sprint 7 step by step!



