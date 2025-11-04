/**
 * @file windows_focus.h
 * @brief Windows window management and focus control
 * 
 * Provides window enumeration and focus management using Win32 API.
 * Demonstrates Windows programming and string matching algorithms.
 */

#pragma once

#ifdef _WIN32

#include <windows.h>
#include <string>
#include <vector>
#include <memory>

namespace jarvis {

/**
 * @struct WindowInfo
 * @brief Information about a window
 */
struct WindowInfo {
    HWND handle;           ///< Window handle
    std::string title;     ///< Window title
    std::string className; ///< Window class name
    bool isVisible;        ///< Window visibility state
};

/**
 * @class WindowManager
 * @brief Manages window enumeration and focus control
 * 
 * Demonstrates:
 * - Win32 API usage
 * - String matching algorithms
 * - Callback patterns
 */
class WindowManager {
public:
    /**
     * @brief Constructor
     */
    WindowManager() = default;
    
    /**
     * @brief Destructor
     */
    ~WindowManager() = default;
    
    /**
     * @brief Focus a window by title (partial match)
     * @param titleSubstring Substring to match in window title
     * @param caseSensitive Whether to perform case-sensitive matching
     * @return True if window found and focused
     * 
     * Algorithm: Boyer-Moore-like substring matching
     * Time complexity: O(n*m) where n=number of windows, m=title length
     * Space complexity: O(n) for window list
     */
    bool focusWindowByTitle(const std::string& titleSubstring, bool caseSensitive = false);
    
    /**
     * @brief Get list of all visible windows
     * @return Vector of WindowInfo structures
     * 
     * Time complexity: O(n) where n=number of windows
     * Space complexity: O(n)
     */
    std::vector<WindowInfo> enumerateWindows();
    
    /**
     * @brief Get information about the foreground window
     * @return WindowInfo for active window
     * 
     * Time complexity: O(1)
     */
    WindowInfo getForegroundWindow();
    
    /**
     * @brief Set window to foreground by handle
     * @param hwnd Window handle
     * @return True if successful
     * 
     * Time complexity: O(1)
     */
    bool setForeground(HWND hwnd);

private:
    /**
     * @brief Get window title as string
     * @param hwnd Window handle
     * @return Window title
     */
    static std::string getWindowTitle(HWND hwnd);
    
    /**
     * @brief Get window class name
     * @param hwnd Window handle
     * @return Class name
     */
    static std::string getWindowClassName(HWND hwnd);
    
    /**
     * @brief Case-insensitive string search
     * @param haystack String to search in
     * @param needle String to search for
     * @return True if needle found in haystack
     * 
     * Time complexity: O(n*m)
     */
    static bool caseInsensitiveSearch(const std::string& haystack, const std::string& needle);
    
    /**
     * @brief Callback for window enumeration
     * @param hwnd Window handle
     * @param lParam User data pointer
     * @return TRUE to continue enumeration
     */
    static BOOL CALLBACK enumWindowsProc(HWND hwnd, LPARAM lParam);
};

} // namespace jarvis

#endif // _WIN32





