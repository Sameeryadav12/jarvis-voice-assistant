/**
 * @file bindings.cpp
 * @brief pybind11 bindings for Jarvis native module
 * 
 * Exposes C++ functionality to Python using pybind11.
 * Demonstrates Python/C++ interoperability.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <memory>
#include <string>

#ifdef _WIN32
#include "audio_endpoint.h"
#include "windows_focus.h"
#endif

namespace py = pybind11;

#ifdef _WIN32

// Global instances (singleton pattern for simplicity)
static std::unique_ptr<jarvis::AudioEndpoint> g_audioEndpoint;
static jarvis::WindowManager g_windowManager;

/**
 * @brief Initialize audio endpoint (lazy initialization)
 */
static void ensureAudioEndpoint() {
    if (!g_audioEndpoint) {
        g_audioEndpoint = std::make_unique<jarvis::AudioEndpoint>();
    }
}

/**
 * @brief Set master volume (Python interface)
 * @param level Volume level (0.0 to 1.0)
 */
void pySetMasterVolume(float level) {
    ensureAudioEndpoint();
    g_audioEndpoint->setMasterVolume(level);
}

/**
 * @brief Get master volume (Python interface)
 * @return Volume level (0.0 to 1.0)
 */
float pyGetMasterVolume() {
    ensureAudioEndpoint();
    return g_audioEndpoint->getMasterVolume();
}

/**
 * @brief Set mute state (Python interface)
 * @param muted True to mute
 */
void pySetMute(bool muted) {
    ensureAudioEndpoint();
    g_audioEndpoint->setMute(muted);
}

/**
 * @brief Get mute state (Python interface)
 * @return True if muted
 */
bool pyGetMute() {
    ensureAudioEndpoint();
    return g_audioEndpoint->getMute();
}

/**
 * @brief Focus window by title (Python interface)
 * @param title Window title or substring
 * @param caseSensitive Whether to match case-sensitively
 * @return True if window found and focused
 */
bool pyFocusWindow(const std::string& title, bool caseSensitive = false) {
    return g_windowManager.focusWindowByTitle(title, caseSensitive);
}

/**
 * @brief Get list of windows (Python interface)
 * @return List of dictionaries with window information
 */
py::list pyEnumerateWindows() {
    auto windows = g_windowManager.enumerateWindows();
    py::list result;
    
    for (const auto& window : windows) {
        py::dict windowDict;
        windowDict["title"] = window.title;
        windowDict["class_name"] = window.className;
        windowDict["is_visible"] = window.isVisible;
        // Don't expose HWND directly to Python for safety
        result.append(windowDict);
    }
    
    return result;
}

#endif // _WIN32

/**
 * @brief Python module definition
 */
PYBIND11_MODULE(jarvis_native, m) {
    m.doc() = "Jarvis native C++ hooks for system control";
    
#ifdef _WIN32
    // Audio control functions
    m.def("set_master_volume", &pySetMasterVolume,
          py::arg("level"),
          "Set system master volume (0.0 to 1.0)");
    
    m.def("get_master_volume", &pyGetMasterVolume,
          "Get system master volume (0.0 to 1.0)");
    
    m.def("set_mute", &pySetMute,
          py::arg("muted"),
          "Set system mute state");
    
    m.def("get_mute", &pyGetMute,
          "Get system mute state");
    
    // Window management functions
    m.def("focus_window", &pyFocusWindow,
          py::arg("title"),
          py::arg("case_sensitive") = false,
          "Focus a window by title (partial match)");
    
    m.def("enumerate_windows", &pyEnumerateWindows,
          "Get list of all visible windows");
    
    // Module info
    m.attr("__version__") = "0.1.0";
    m.attr("platform") = "Windows";
    
#else
    // Non-Windows platforms - provide stub functions
    m.def("set_master_volume", [](float level) {
        throw std::runtime_error("Not implemented on this platform");
    });
    m.def("get_master_volume", []() -> float {
        throw std::runtime_error("Not implemented on this platform");
    });
    m.def("focus_window", [](const std::string& title, bool cs) -> bool {
        throw std::runtime_error("Not implemented on this platform");
    });
    
    m.attr("__version__") = "0.1.0";
    m.attr("platform") = "Unsupported";
#endif
}



