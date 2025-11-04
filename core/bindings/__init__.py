"""
Native bindings module for system control.
Provides C++ or Python fallback implementations.
"""

try:
    # Try to import C++ module first
    import jarvis_native
    __all__ = ["jarvis_native"]
    __implementation__ = "C++"
except ImportError:
    # Fall back to Python ctypes
    from . import windows_native
    __all__ = ["windows_native"]
    __implementation__ = "Python (ctypes)"




