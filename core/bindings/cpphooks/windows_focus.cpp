/**
 * @file windows_focus.cpp
 * @brief Implementation of Windows window management
 */

#include "windows_focus.h"

#ifdef _WIN32

#include <algorithm>
#include <cctype>
#include <stdexcept>

namespace jarvis {

std::string WindowManager::getWindowTitle(HWND hwnd) {
    int length = GetWindowTextLengthW(hwnd);
    if (length == 0) {
        return "";
    }
    
    std::wstring wideTitle(length + 1, L'\0');
    GetWindowTextW(hwnd, &wideTitle[0], length + 1);
    
    // Convert wide string to UTF-8
    int size = WideCharToMultiByte(CP_UTF8, 0, wideTitle.c_str(), -1, nullptr, 0, nullptr, nullptr);
    std::string result(size - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wideTitle.c_str(), -1, &result[0], size, nullptr, nullptr);
    
    return result;
}

std::string WindowManager::getWindowClassName(HWND hwnd) {
    wchar_t className[256] = {0};
    GetClassNameW(hwnd, className, 256);
    
    // Convert to UTF-8
    int size = WideCharToMultiByte(CP_UTF8, 0, className, -1, nullptr, 0, nullptr, nullptr);
    std::string result(size - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, className, -1, &result[0], size, nullptr, nullptr);
    
    return result;
}

bool WindowManager::caseInsensitiveSearch(const std::string& haystack, const std::string& needle) {
    // Convert both to lowercase for comparison
    std::string haystackLower = haystack;
    std::string needleLower = needle;
    
    std::transform(haystackLower.begin(), haystackLower.end(), haystackLower.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    std::transform(needleLower.begin(), needleLower.end(), needleLower.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    
    return haystackLower.find(needleLower) != std::string::npos;
}

BOOL CALLBACK WindowManager::enumWindowsProc(HWND hwnd, LPARAM lParam) {
    auto* windows = reinterpret_cast<std::vector<WindowInfo>*>(lParam);
    
    // Only include visible windows with titles
    if (!IsWindowVisible(hwnd)) {
        return TRUE;
    }
    
    std::string title = getWindowTitle(hwnd);
    if (title.empty()) {
        return TRUE;
    }
    
    WindowInfo info;
    info.handle = hwnd;
    info.title = title;
    info.className = getWindowClassName(hwnd);
    info.isVisible = true;
    
    windows->push_back(info);
    return TRUE;
}

std::vector<WindowInfo> WindowManager::enumerateWindows() {
    std::vector<WindowInfo> windows;
    EnumWindows(enumWindowsProc, reinterpret_cast<LPARAM>(&windows));
    return windows;
}

WindowInfo WindowManager::getForegroundWindow() {
    HWND hwnd = ::GetForegroundWindow();
    
    WindowInfo info;
    info.handle = hwnd;
    info.title = getWindowTitle(hwnd);
    info.className = getWindowClassName(hwnd);
    info.isVisible = IsWindowVisible(hwnd) != FALSE;
    
    return info;
}

bool WindowManager::setForeground(HWND hwnd) {
    if (!IsWindow(hwnd)) {
        return false;
    }
    
    // Restore if minimized
    if (IsIconic(hwnd)) {
        ShowWindow(hwnd, SW_RESTORE);
    }
    
    // Try to set foreground
    // This might fail due to Windows security restrictions
    if (!SetForegroundWindow(hwnd)) {
        // Try alternative method
        DWORD currentThread = GetCurrentThreadId();
        DWORD windowThread = GetWindowThreadProcessId(hwnd, nullptr);
        
        // Attach to window's thread
        AttachThreadInput(currentThread, windowThread, TRUE);
        SetForegroundWindow(hwnd);
        AttachThreadInput(currentThread, windowThread, FALSE);
    }
    
    return GetForegroundWindow() == hwnd;
}

bool WindowManager::focusWindowByTitle(const std::string& titleSubstring, bool caseSensitive) {
    std::vector<WindowInfo> windows = enumerateWindows();
    
    // Search for matching window
    // Demonstrates linear search with string matching
    // Time complexity: O(n) where n is number of windows
    for (const auto& window : windows) {
        bool matches = false;
        
        if (caseSensitive) {
            matches = window.title.find(titleSubstring) != std::string::npos;
        } else {
            matches = caseInsensitiveSearch(window.title, titleSubstring);
        }
        
        if (matches) {
            return setForeground(window.handle);
        }
    }
    
    return false;
}

} // namespace jarvis

#endif // _WIN32





