"""
Audio processing module for Jarvis.
Handles microphone capture, wake word detection, and STT integration.
"""

from .capture import AudioCapture
from .wakeword import WakeWordDetector
from .audio_pipeline import AudioPipeline, PipelineState
from .stt_offline import WhisperSTT
from .stt_realtime import RealtimeSTT
from .stt_faster_whisper import FasterWhisperSTT, create_faster_whisper
from .stt_backend import STTBackendManager, STTBackendType, create_stt_backend_manager
from .audio_buffer import AudioRingBuffer, VadGatedAudioBuffer
from .vad import SileroVAD, create_vad
from .vad_profiles import VADProfiler, MicrophoneProfile, create_default_profiler
from .stt_partial import (
    PartialResultStreamer,
    FasterWhisperPartialStreamer,
    PartialResult,
    create_partial_streamer,
)
from .barge_in import (
    BargeInDetector,
    TTSBargeInManager,
    create_barge_in_detector,
)

__all__ = [
    "AudioCapture",
    "WakeWordDetector", 
    "AudioPipeline",
    "PipelineState",
    "WhisperSTT",
    "RealtimeSTT",
    "FasterWhisperSTT",
    "create_faster_whisper",
    "STTBackendManager",
    "STTBackendType",
    "create_stt_backend_manager",
    "AudioRingBuffer",
    "VadGatedAudioBuffer",
    "SileroVAD",
    "create_vad",
    "VADProfiler",
    "MicrophoneProfile",
    "create_default_profiler",
    "PartialResultStreamer",
    "FasterWhisperPartialStreamer",
    "PartialResult",
    "create_partial_streamer",
    "BargeInDetector",
    "TTSBargeInManager",
    "create_barge_in_detector",
]

