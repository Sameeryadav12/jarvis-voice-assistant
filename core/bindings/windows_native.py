"""
Windows native API using pycaw library.
Provides volume control and window management without C++ compilation.
"""

import sys
from typing import List, Dict
from loguru import logger

if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False


    class WindowsAudio:
        """Windows audio control using pycaw."""
        
        def __init__(self):
            """Initialize Windows audio control."""
            if not PYCAW_AVAILABLE:
                raise ImportError("pycaw library not available")
            
            self.volume = None
            self._initialize()
        
        def _initialize(self):
            """Initialize audio interface."""
            try:
                devices = AudioUtilities.GetSpeakers()
                self.volume = devices.EndpointVolume
                logger.info("Windows audio initialized (pycaw)")
            except Exception as e:
                logger.error(f"Audio init failed: {e}")
                raise
        
        def set_master_volume(self, level: float) -> None:
            """Set volume (0.0 to 1.0)."""
            if not 0.0 <= level <= 1.0:
                raise ValueError("Level must be 0.0-1.0")
            self.volume.SetMasterVolumeLevelScalar(level, None)
        
        def get_master_volume(self) -> float:
            """Get volume (0.0 to 1.0)."""
            return self.volume.GetMasterVolumeLevelScalar()
        
        def set_mute(self, muted: bool) -> None:
            """Set mute state."""
            self.volume.SetMute(1 if muted else 0, None)
        
        def get_mute(self) -> bool:
            """Get mute state."""
            return bool(self.volume.GetMute())


    class WindowsWindowManager:
        """Windows window management using Win32 API."""
        
        def __init__(self):
            """Initialize window manager."""
            self.user32 = ctypes.windll.user32
            logger.info("Windows window manager initialized")
        
        def focus_window(self, title_substring: str, case_sensitive: bool = False) -> bool:
            """Focus window by title substring."""
            def enum_callback(hwnd, param):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True
                
                buffer = ctypes.create_unicode_buffer(length + 1)
                self.user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                
                if not title or not self.user32.IsWindowVisible(hwnd):
                    return True
                
                matches = title_substring in title if case_sensitive else title_substring.lower() in title.lower()
                
                if matches:
                    param[0] = hwnd
                    return False
                return True
            
            hwnd_found = [None]
            EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            callback = EnumWindowsProc(enum_callback)
            self.user32.EnumWindows(callback, id(hwnd_found))
            
            if hwnd_found[0]:
                if self.user32.IsIconic(hwnd_found[0]):
                    self.user32.ShowWindow(hwnd_found[0], 9)
                self.user32.SetForegroundWindow(hwnd_found[0])
                logger.info(f"Focused window: '{title_substring}'")
                return True
            return False
        
        def enumerate_windows(self) -> List[Dict]:
            """Get list of visible windows."""
            windows = []
            
            def enum_callback(hwnd, param):
                if not self.user32.IsWindowVisible(hwnd):
                    return True
                
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True
                
                buffer = ctypes.create_unicode_buffer(length + 1)
                self.user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                
                if title:
                    windows.append({'title': title, 'hwnd': hwnd})
                return True
            
            EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            callback = EnumWindowsProc(enum_callback)
            self.user32.EnumWindows(callback, 0)
            return windows


    # Singleton instances
    _audio = None
    _window_manager = None


    def _get_audio():
        global _audio
        if _audio is None:
            _audio = WindowsAudio()
        return _audio


    def _get_window_manager():
        global _window_manager
        if _window_manager is None:
            _window_manager = WindowsWindowManager()
        return _window_manager


    # Public API
    def set_master_volume(level: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        _get_audio().set_master_volume(level)


    def get_master_volume() -> float:
        """Get master volume (0.0 to 1.0)."""
        return _get_audio().get_master_volume()


    def set_mute(muted: bool) -> None:
        """Set mute state."""
        _get_audio().set_mute(muted)


    def get_mute() -> bool:
        """Get mute state."""
        return _get_audio().get_mute()


    def focus_window(title: str, case_sensitive: bool = False) -> bool:
        """Focus window by title."""
        return _get_window_manager().focus_window(title, case_sensitive)


    def enumerate_windows() -> List[Dict]:
        """Get list of windows."""
        return _get_window_manager().enumerate_windows()


else:
    # Non-Windows stub
    def set_master_volume(level: float) -> None:
        raise NotImplementedError("Not implemented on this platform")
    
    def get_master_volume() -> float:
        raise NotImplementedError("Not implemented on this platform")
    
    def set_mute(muted: bool) -> None:
        raise NotImplementedError("Not implemented on this platform")
    
    def get_mute() -> bool:
        raise NotImplementedError("Not implemented on this platform")
    
    def focus_window(title: str, case_sensitive: bool = False) -> bool:
        raise NotImplementedError("Not implemented on this platform")
    
    def enumerate_windows() -> List[Dict]:
        raise NotImplementedError("Not implemented on this platform")


__version__ = "0.1.0"
__platform__ = "Windows (pycaw)" if sys.platform == 'win32' else "Unsupported"
