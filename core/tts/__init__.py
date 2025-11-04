"""
Text-to-Speech module for Jarvis.
Supports multiple TTS backends (Piper, Edge TTS, Coqui).
"""

from .piper import PiperTTS
from .edge import EdgeTTS

__all__ = ["PiperTTS", "EdgeTTS"]





