"""
VAD Microphone Profile Detection and Calibration

Auto-detects microphone characteristics and tunes VAD thresholds
for optimal speech detection per device.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import sounddevice as sd
from loguru import logger
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.audio.vad import SileroVAD


class MicrophoneProfile:
    """Stores calibrated profile for a microphone."""
    
    def __init__(
        self,
        device_id: int,
        device_name: str,
        threshold: float,
        min_speech_duration_ms: int,
        min_silence_duration_ms: int,
        noise_level: float,
        sensitivity: float = 1.0,
    ):
        """
        Initialize microphone profile.
        
        Args:
            device_id: Audio device ID
            device_name: Device name
            threshold: Calibrated VAD threshold
            min_speech_duration_ms: Minimum speech duration
            min_silence_duration_ms: Minimum silence duration
            noise_level: Measured background noise level (0.0-1.0)
            sensitivity: Device sensitivity multiplier
        """
        self.device_id = device_id
        self.device_name = device_name
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.noise_level = noise_level
        self.sensitivity = sensitivity
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "threshold": self.threshold,
            "min_speech_duration_ms": self.min_speech_duration_ms,
            "min_silence_duration_ms": self.min_silence_duration_ms,
            "noise_level": self.noise_level,
            "sensitivity": self.sensitivity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MicrophoneProfile':
        """Create from dictionary."""
        return cls(**data)


class VADProfiler:
    """
    Auto-detects microphone characteristics and calibrates VAD settings.
    
    Features:
    - Noise level measurement
    - Automatic threshold tuning
    - Device-specific profiles
    - Persistent storage
    """
    
    def __init__(self, profiles_file: Optional[Path] = None):
        """
        Initialize VAD profiler.
        
        Args:
            profiles_file: Path to store profiles JSON (default: user config)
        """
        if profiles_file is None:
            profiles_file = Path.home() / ".jarvis" / "vad_profiles.json"
        
        self.profiles_file = profiles_file
        self.profiles: Dict[int, MicrophoneProfile] = {}
        
        # Ensure directory exists
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles
        self.load_profiles()
    
    def load_profiles(self):
        """Load profiles from disk."""
        if not self.profiles_file.exists():
            logger.info(f"No existing VAD profiles found at {self.profiles_file}")
            return
        
        try:
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)
            
            for device_id, profile_data in data.items():
                profile = MicrophoneProfile.from_dict(profile_data)
                self.profiles[int(device_id)] = profile
            
            logger.info(f"Loaded {len(self.profiles)} VAD profiles")
        except Exception as e:
            logger.warning(f"Failed to load VAD profiles: {e}")
    
    def save_profiles(self):
        """Save profiles to disk."""
        try:
            data = {
                str(device_id): profile.to_dict()
                for device_id, profile in self.profiles.items()
            }
            
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.profiles)} VAD profiles")
        except Exception as e:
            logger.error(f"Failed to save VAD profiles: {e}")
    
    def measure_noise_level(
        self,
        device_id: Optional[int] = None,
        duration_seconds: float = 2.0,
        sample_rate: int = 16000,
    ) -> float:
        """
        Measure background noise level of microphone.
        
        Args:
            device_id: Audio device ID (default: default input)
            duration_seconds: Duration to record for measurement
            sample_rate: Audio sample rate
            
        Returns:
            Noise level (0.0-1.0)
        """
        logger.info(f"Measuring noise level for device {device_id}...")
        
        try:
            # Record silence/background noise
            samples = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_id,
                dtype=np.float32,
            )
            sd.wait()
            
            # Calculate RMS (root mean square) amplitude
            rms = np.sqrt(np.mean(samples ** 2))
            
            # Normalize to 0.0-1.0
            noise_level = min(1.0, max(0.0, rms * 10.0))  # Scale factor
            
            logger.info(f"Measured noise level: {noise_level:.3f}")
            return noise_level
            
        except Exception as e:
            logger.error(f"Failed to measure noise level: {e}")
            return 0.1  # Default fallback
    
    def calibrate_threshold(
        self,
        noise_level: float,
        target_false_positive_rate: float = 0.01,
    ) -> float:
        """
        Calculate optimal VAD threshold based on noise level.
        
        Args:
            noise_level: Measured background noise (0.0-1.0)
            target_false_positive_rate: Desired false positive rate
            
        Returns:
            Calibrated threshold (0.0-1.0)
        """
        # Base threshold
        base_threshold = 0.5
        
        # Adjust based on noise level
        # Higher noise = higher threshold needed
        noise_adjustment = noise_level * 0.3
        
        # Calculate threshold
        threshold = base_threshold + noise_adjustment
        
        # Adjust for false positive rate
        # Lower FPR = higher threshold
        fpr_adjustment = (1.0 - target_false_positive_rate) * 0.2
        threshold += fpr_adjustment
        
        # Clamp to valid range
        threshold = min(0.9, max(0.3, threshold))
        
        logger.info(f"Calibrated threshold: {threshold:.3f} (noise: {noise_level:.3f})")
        return threshold
    
    def create_profile(
        self,
        device_id: Optional[int] = None,
        device_name: Optional[str] = None,
        calibration_duration: float = 2.0,
    ) -> MicrophoneProfile:
        """
        Create a calibrated profile for a microphone.
        
        Args:
            device_id: Audio device ID (default: default input)
            device_name: Device name (auto-detected if None)
            calibration_duration: Duration for noise measurement
            
        Returns:
            Calibrated microphone profile
        """
        if device_id is None:
            device_id = sd.default.device[0]
        
        if device_name is None:
            device_info = sd.query_devices(device_id)
            device_name = device_info['name']
        
        logger.info(f"Creating profile for device {device_id}: {device_name}")
        
        # Measure noise level
        noise_level = self.measure_noise_level(
            device_id=device_id,
            duration_seconds=calibration_duration,
        )
        
        # Calibrate threshold
        threshold = self.calibrate_threshold(noise_level)
        
        # Adjust durations based on noise
        # Noisy environments need longer speech/silence durations
        if noise_level > 0.3:
            min_speech_duration_ms = 300  # Longer for noisy
            min_silence_duration_ms = 600
        else:
            min_speech_duration_ms = 250  # Standard
            min_silence_duration_ms = 500
        
        # Calculate sensitivity (how sensitive the mic is)
        # Based on noise level and device gain
        sensitivity = 1.0 / (1.0 + noise_level)
        
        profile = MicrophoneProfile(
            device_id=device_id,
            device_name=device_name,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            noise_level=noise_level,
            sensitivity=sensitivity,
        )
        
        # Store profile
        self.profiles[device_id] = profile
        self.save_profiles()
        
        logger.info(f"Profile created: threshold={threshold:.3f}, noise={noise_level:.3f}")
        return profile
    
    def get_profile(self, device_id: Optional[int] = None) -> Optional[MicrophoneProfile]:
        """
        Get profile for device, creating if doesn't exist.
        
        Args:
            device_id: Audio device ID (default: default input)
            
        Returns:
            Microphone profile or None if creation fails
        """
        if device_id is None:
            device_id = sd.default.device[0]
        
        if device_id in self.profiles:
            return self.profiles[device_id]
        
        # Auto-create profile if missing
        logger.info(f"No profile found for device {device_id}, creating one...")
        try:
            return self.create_profile(device_id=device_id)
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            return None
    
    def apply_profile(self, vad: SileroVAD, device_id: Optional[int] = None):
        """
        Apply profile settings to a VAD instance.
        
        Args:
            vad: SileroVAD instance to configure
            device_id: Audio device ID (default: default input)
        """
        profile = self.get_profile(device_id=device_id)
        if profile is None:
            logger.warning("No profile available, using default VAD settings")
            return
        
        # Apply calibrated settings
        vad.threshold = profile.threshold
        vad.min_speech_duration_ms = profile.min_speech_duration_ms
        vad.min_silence_duration_ms = profile.min_silence_duration_ms
        
        logger.info(
            f"Applied profile: threshold={profile.threshold:.3f}, "
            f"speech_ms={profile.min_speech_duration_ms}, "
            f"silence_ms={profile.min_silence_duration_ms}"
        )
    
    def list_profiles(self) -> Dict[int, MicrophoneProfile]:
        """List all stored profiles."""
        return self.profiles.copy()
    
    def delete_profile(self, device_id: int):
        """Delete a profile."""
        if device_id in self.profiles:
            del self.profiles[device_id]
            self.save_profiles()
            logger.info(f"Deleted profile for device {device_id}")


def create_default_profiler() -> VADProfiler:
    """Create a default VAD profiler instance."""
    return VADProfiler()

