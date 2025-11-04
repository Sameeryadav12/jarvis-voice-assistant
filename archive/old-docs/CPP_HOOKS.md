# C++ Hooks Developer Guide

## Overview

Jarvis uses C++ for low-level system operations where performance and direct OS API access are critical. This document explains the C++ hook system and how to extend it.

## Why C++?

1. **Performance**: <10ms latency for system operations
2. **Direct API Access**: WASAPI, Win32 without FFI overhead
3. **Type Safety**: Compile-time checks for system APIs
4. **Resume-Friendly**: Shows systems programming skills

## Architecture

```
Python Code                 pybind11                C++ Code                OS API
-----------                 --------                --------                ------
set_volume(0.5) → jarvis_native.set_master_volume() → AudioEndpoint → IAudioEndpointVolume
                                                     → setMasterVolume()  → SetMasterVolumeLevelScalar()
```

## Project Structure

```
core/bindings/cpphooks/
├── CMakeLists.txt           # Build configuration
├── audio_endpoint.h         # Volume control interface
├── audio_endpoint.cpp       # Volume control implementation
├── windows_focus.h          # Window management interface
├── windows_focus.cpp        # Window management implementation
├── bindings.cpp             # pybind11 Python bindings
└── pybind11/                # pybind11 submodule
```

## Building

### Windows

**Prerequisites**:
- Visual Studio 2019+ with C++ tools
- CMake 3.20+
- Python 3.10+ with development headers

**Build Steps**:
```powershell
cd core/bindings/cpphooks
git clone https://github.com/pybind/pybind11.git
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

**Output**: `jarvis_native.pyd` in project root

### Linux/macOS

**Prerequisites**:
- GCC/Clang with C++17 support
- CMake 3.20+
- Python 3.10+ development headers

**Build Steps**:
```bash
cd core/bindings/cpphooks
git clone https://github.com/pybind/pybind11.git
mkdir build
cd build
cmake ..
make -j$(nproc)
```

**Output**: `jarvis_native.so` in project root

## Audio Control (WASAPI)

### Interface (audio_endpoint.h)

```cpp
class AudioEndpoint {
public:
    AudioEndpoint();  // Initialize COM, get endpoint
    ~AudioEndpoint(); // Cleanup COM resources
    
    void setMasterVolume(float level);  // 0.0 to 1.0
    float getMasterVolume() const;
    void setMute(bool muted);
    bool getMute() const;
private:
    IMMDeviceEnumerator* deviceEnumerator_;
    IMMDevice* device_;
    IAudioEndpointVolume* endpointVolume_;
    bool comInitialized_;
};
```

### Implementation Highlights

#### RAII Pattern

```cpp
AudioEndpoint::AudioEndpoint() {
    initialize();  // Acquire resources
}

AudioEndpoint::~AudioEndpoint() {
    cleanup();     // Release resources automatically
}
```

**Benefits**:
- No memory leaks
- Exception-safe
- Clear ownership semantics

#### COM Initialization

```cpp
void AudioEndpoint::initialize() {
    // 1. Initialize COM
    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) {
        throw std::runtime_error("Failed to initialize COM");
    }
    
    // 2. Create device enumerator
    hr = CoCreateInstance(
        __uuidof(MMDeviceEnumerator),
        nullptr, CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator),
        reinterpret_cast<void**>(&deviceEnumerator_)
    );
    
    // 3. Get default audio endpoint
    hr = deviceEnumerator_->GetDefaultAudioEndpoint(
        eRender,   // Playback devices
        eConsole,  // Console role
        &device_
    );
    
    // 4. Activate volume interface
    hr = device_->Activate(
        __uuidof(IAudioEndpointVolume),
        CLSCTX_ALL, nullptr,
        reinterpret_cast<void**>(&endpointVolume_)
    );
}
```

#### Volume Control

```cpp
void AudioEndpoint::setMasterVolume(float level) {
    // Validate input
    if (level < 0.0f || level > 1.0f) {
        throw std::invalid_argument("Volume must be 0.0-1.0");
    }
    
    // Set volume (0.0 = silent, 1.0 = max)
    HRESULT hr = endpointVolume_->SetMasterVolumeLevelScalar(
        level,
        nullptr  // Event context (not used)
    );
    
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to set volume");
    }
}
```

**Time Complexity**: O(1)
**Space Complexity**: O(1)

### Python Binding

```cpp
PYBIND11_MODULE(jarvis_native, m) {
    m.def("set_master_volume", &pySetMasterVolume,
          py::arg("level"),
          "Set system master volume (0.0 to 1.0)");
    
    m.def("get_master_volume", &pyGetMasterVolume,
          "Get system master volume");
}
```

### Usage from Python

```python
import jarvis_native

# Set volume to 50%
jarvis_native.set_master_volume(0.5)

# Get current volume
volume = jarvis_native.get_master_volume()
print(f"Current volume: {volume * 100}%")

# Mute
jarvis_native.set_mute(True)
```

## Window Management (Win32)

### Interface (windows_focus.h)

```cpp
struct WindowInfo {
    HWND handle;
    std::string title;
    std::string className;
    bool isVisible;
};

class WindowManager {
public:
    bool focusWindowByTitle(
        const std::string& titleSubstring,
        bool caseSensitive = false
    );
    
    std::vector<WindowInfo> enumerateWindows();
    WindowInfo getForegroundWindow();
    bool setForeground(HWND hwnd);
};
```

### Implementation Highlights

#### Window Enumeration

```cpp
std::vector<WindowInfo> WindowManager::enumerateWindows() {
    std::vector<WindowInfo> windows;
    
    // Windows callback-based enumeration
    EnumWindows(
        enumWindowsProc,
        reinterpret_cast<LPARAM>(&windows)
    );
    
    return windows;
}

// Callback function
BOOL CALLBACK WindowManager::enumWindowsProc(
    HWND hwnd,
    LPARAM lParam
) {
    auto* windows = reinterpret_cast<std::vector<WindowInfo>*>(lParam);
    
    // Filter: visible windows with titles
    if (!IsWindowVisible(hwnd)) return TRUE;
    
    std::string title = getWindowTitle(hwnd);
    if (title.empty()) return TRUE;
    
    // Add to list
    windows->push_back({
        hwnd,
        title,
        getWindowClassName(hwnd),
        true
    });
    
    return TRUE;  // Continue enumeration
}
```

**Time Complexity**: O(n) where n = number of windows
**Space Complexity**: O(n)

#### String Matching

```cpp
bool WindowManager::caseInsensitiveSearch(
    const std::string& haystack,
    const std::string& needle
) {
    // Convert both to lowercase
    std::string haystackLower = haystack;
    std::string needleLower = needle;
    
    std::transform(
        haystackLower.begin(), haystackLower.end(),
        haystackLower.begin(),
        [](unsigned char c) { return std::tolower(c); }
    );
    
    std::transform(
        needleLower.begin(), needleLower.end(),
        needleLower.begin(),
        [](unsigned char c) { return std::tolower(c); }
    );
    
    return haystackLower.find(needleLower) != std::string::npos;
}
```

**Time Complexity**: O(n + m) where n, m = string lengths
**Space Complexity**: O(n + m)

#### Focus Window

```cpp
bool WindowManager::focusWindowByTitle(
    const std::string& titleSubstring,
    bool caseSensitive
) {
    // Get all windows
    std::vector<WindowInfo> windows = enumerateWindows();
    
    // Linear search with string matching
    for (const auto& window : windows) {
        bool matches = caseSensitive
            ? (window.title.find(titleSubstring) != std::string::npos)
            : caseInsensitiveSearch(window.title, titleSubstring);
        
        if (matches) {
            return setForeground(window.handle);
        }
    }
    
    return false;  // Not found
}
```

### Usage from Python

```python
import jarvis_native

# Focus Visual Studio
jarvis_native.focus_window("Visual Studio")

# List all windows
windows = jarvis_native.enumerate_windows()
for window in windows:
    print(f"Title: {window['title']}")
```

## Adding New Hooks

### Step 1: Define C++ Interface

Create header file (e.g., `keyboard.h`):

```cpp
#pragma once

#ifdef _WIN32
#include <windows.h>

namespace jarvis {

class KeyboardManager {
public:
    void sendKeyPress(int virtualKeyCode);
    void sendText(const std::string& text);
    bool isKeyPressed(int virtualKeyCode);
};

} // namespace jarvis
#endif
```

### Step 2: Implement Functionality

Create implementation file (e.g., `keyboard.cpp`):

```cpp
#include "keyboard.h"

namespace jarvis {

void KeyboardManager::sendKeyPress(int vk) {
    // Simulate key press
    keybd_event(vk, 0, 0, 0);
    keybd_event(vk, 0, KEYEVENTF_KEYUP, 0);
}

void KeyboardManager::sendText(const std::string& text) {
    for (char c : text) {
        SHORT vk = VkKeyScanA(c);
        sendKeyPress(LOBYTE(vk));
    }
}

bool KeyboardManager::isKeyPressed(int vk) {
    return GetAsyncKeyState(vk) & 0x8000;
}

} // namespace jarvis
```

### Step 3: Add pybind11 Bindings

Update `bindings.cpp`:

```cpp
#include "keyboard.h"

static jarvis::KeyboardManager g_keyboardManager;

void pySendKeyPress(int vk) {
    g_keyboardManager.sendKeyPress(vk);
}

PYBIND11_MODULE(jarvis_native, m) {
    // ... existing bindings ...
    
    m.def("send_key_press", &pySendKeyPress,
          py::arg("virtual_key_code"),
          "Send a key press event");
}
```

### Step 4: Update CMakeLists.txt

Add new source files:

```cmake
set(SOURCES
    bindings.cpp
    audio_endpoint.cpp
    windows_focus.cpp
    keyboard.cpp  # New file
)
```

### Step 5: Rebuild

```bash
cd build
cmake --build . --config Release
```

### Step 6: Use from Python

```python
import jarvis_native

# Send Enter key
VK_RETURN = 0x0D
jarvis_native.send_key_press(VK_RETURN)
```

## Best Practices

### 1. RAII Everything

```cpp
// Good: Resources automatically cleaned up
class Resource {
public:
    Resource() { acquire(); }
    ~Resource() { release(); }
};

// Bad: Manual cleanup (error-prone)
void func() {
    Resource* r = new Resource();
    // ... use r ...
    delete r;  // Easy to forget!
}
```

### 2. Exception Safety

```cpp
// Strong guarantee: either succeeds or no effect
void AudioEndpoint::setMasterVolume(float level) {
    // 1. Validate first (no side effects)
    if (level < 0.0f || level > 1.0f) {
        throw std::invalid_argument("Invalid level");
    }
    
    // 2. Then modify state
    HRESULT hr = endpointVolume_->SetMasterVolumeLevelScalar(level, nullptr);
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to set volume");
    }
}
```

### 3. Move Semantics

```cpp
class AudioEndpoint {
public:
    // Disable copying (COM objects shouldn't be copied)
    AudioEndpoint(const AudioEndpoint&) = delete;
    AudioEndpoint& operator=(const AudioEndpoint&) = delete;
    
    // Enable moving (transfer ownership)
    AudioEndpoint(AudioEndpoint&&) noexcept = default;
    AudioEndpoint& operator=(AudioEndpoint&&) noexcept = default;
};
```

### 4. Const Correctness

```cpp
class AudioEndpoint {
public:
    // Doesn't modify state
    float getMasterVolume() const;
    
    // Modifies state
    void setMasterVolume(float level);
};
```

### 5. Error Messages

```cpp
// Good: Descriptive error with context
throw std::runtime_error(
    "Failed to set volume: " + HResultToString(hr)
);

// Bad: Vague error
throw std::runtime_error("Error");
```

## Testing C++ Code

### Unit Tests (Catch2)

```cpp
#include <catch2/catch.hpp>
#include "audio_endpoint.h"

TEST_CASE("Volume control", "[audio]") {
    AudioEndpoint endpoint;
    
    SECTION("Set valid volume") {
        endpoint.setMasterVolume(0.5f);
        REQUIRE(endpoint.getMasterVolume() == Approx(0.5f));
    }
    
    SECTION("Reject invalid volume") {
        REQUIRE_THROWS_AS(
            endpoint.setMasterVolume(1.5f),
            std::invalid_argument
        );
    }
}
```

### Memory Leak Detection

**Windows**: Visual Studio Diagnostic Tools
**Linux**: Valgrind

```bash
valgrind --leak-check=full python -c "
import jarvis_native
jarvis_native.set_master_volume(0.5)
"
```

## Performance Optimization

### 1. Avoid Unnecessary Copies

```cpp
// Good: Pass by const reference
void processWindow(const WindowInfo& window);

// Bad: Pass by value (copies entire struct)
void processWindow(WindowInfo window);
```

### 2. Reserve Vector Capacity

```cpp
std::vector<WindowInfo> windows;
windows.reserve(100);  // Avoid reallocations
```

### 3. Use String Views (C++17)

```cpp
bool contains(std::string_view haystack, std::string_view needle) {
    // No string copies!
    return haystack.find(needle) != std::string_view::npos;
}
```

## Platform Support

### Windows

- ✅ Volume control (WASAPI)
- ✅ Window management (Win32)
- ✅ Keyboard simulation (SendInput)
- ⏳ Media keys (planned)

### macOS

- ⏳ Volume control (CoreAudio)
- ⏳ Window management (Accessibility API)
- ⏳ AppleScript integration

### Linux

- ⏳ Volume control (PulseAudio)
- ⏳ Window management (wmctrl)
- ⏳ X11/Wayland support

## Troubleshooting

### Build Fails: "pybind11 not found"

```bash
cd core/bindings/cpphooks
git clone https://github.com/pybind/pybind11.git
```

### Build Fails: "Python.h not found"

Install Python development headers:
- **Windows**: Included with Python installer
- **Ubuntu**: `sudo apt-get install python3-dev`
- **macOS**: `brew install python`

### Module Import Error

Ensure `jarvis_native.pyd` (or `.so`) is in:
- Project root, or
- Python's site-packages, or
- A directory in `sys.path`

### COM Initialization Fails

Run Python as administrator on Windows (required for some WASAPI operations).

## Resources

- **WASAPI**: [Microsoft Docs - Core Audio APIs](https://learn.microsoft.com/en-us/windows/win32/coreaudio/core-audio-apis-in-windows-vista)
- **Win32**: [Microsoft Docs - Desktop App Development](https://learn.microsoft.com/en-us/windows/win32/)
- **pybind11**: [pybind11 Documentation](https://pybind11.readthedocs.io/)
- **COM**: [The COM Programming Guide](https://learn.microsoft.com/en-us/windows/win32/com/)





