"""
Configuration Manager

Loads, validates, and manages application settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger


class ConfigManager:
    """
    Configuration manager for Jarvis.
    
    Loads settings from YAML files with validation and defaults.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config file (default: config/settings.yaml)
        """
        # Determine config path
        if config_path is None:
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "config" / "settings.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Using default configuration")
            self.config = self._get_defaults()
            self._save_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            # Merge with defaults
            defaults = self._get_defaults()
            self.config = self._merge_configs(defaults, self.config)
            
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'general': {
                'app_name': 'Jarvis',
                'version': '0.1.0',
                'log_level': 'INFO',
                'log_file': 'logs/jarvis.log',
                'offline_mode': False  # Offline mode toggle
            },
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'chunk_duration_ms': 30,
                'buffer_size_seconds': 10,
                'input_device': None,
                'output_device': None
            },
            'wake_word': {
                'enabled': False,
                'access_key': '',
                'keyword': 'jarvis',
                'sensitivity': 0.5,
                'custom_keyword_path': None
            },
            'stt': {
                'mode': 'offline',
                'offline': {
                    'model_path': 'models/ggml-base.en.bin',
                    'binary_path': 'whisper-cpp/main',
                    'language': 'en',
                    'num_threads': 4
                },
                'cloud': {
                    'api_key': '',
                    'model': 'gpt-4o-realtime-preview-2024-10-01',
                    'voice': 'alloy',
                    'temperature': 0.8
                }
            },
            'nlu': {
                'spacy_model': 'en_core_web_sm',
                'confidence_threshold': 0.5,
                'custom_patterns': None
            },
            'tts': {
                'mode': 'edge',  # Changed to edge for cloud TTS
                'piper': {
                    'model_path': 'models/piper/en_US-lessac-medium.onnx',
                    'binary_path': 'piper/piper',
                    'sample_rate': 22050
                },
                'edge': {
                    'voice': 'en-US-AriaNeural',
                    'rate': '+0%',
                    'volume': '+0%'
                }
            },
            'memory': {
                'enabled': True,
                'persist_directory': './chroma_db',
                'collection_name': 'jarvis_memory',
                'max_context_items': 10,
                'auto_save_conversation': True
            },
            'skills': {
                'system': {'enabled': True},
                'calendar': {
                    'enabled': False,
                    'credentials_file': 'credentials.json',
                    'timezone': 'America/Los_Angeles'
                },
                'reminders': {
                    'enabled': True,
                    'persistent': False
                },
                'web': {
                    'enabled': False,
                    'headless': True
                }
            },
            'notifications': {
                'enabled': True
            },
            'ui': {
                'enabled': True,
                'width': 800,
                'height': 600,
                'always_on_top': False,
                'start_minimized': False,
                'theme': 'dark',
                'update_interval': 100
            },
            'hotkeys': {
                'push_to_talk': None,
                'toggle_ui': 'ctrl+shift+j',
                'mute_toggle': None
            },
            'security': {
                'encrypt_credentials': True,
                'require_confirmation': ['system.volume', 'web.automation'],
                'allowed_skills': []
            },
            'telemetry': {
                'enabled': False,
                'anonymous': True,
                'endpoint': None
            },
            'advanced': {
                'debug': False,
                'profile': False,
                'auto_restart': False,
                'max_memory_mb': 1024
            }
        }
    
    def _merge_configs(self, defaults: Dict, user_config: Dict) -> Dict:
        """Recursively merge user config into defaults."""
        result = defaults.copy()
        
        for key, value in user_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_default_config(self) -> None:
        """Save default configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Created default config at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def is_offline_mode(self) -> bool:
        """
        Check if offline mode is enabled.
        
        Returns:
            True if offline mode is enabled
        """
        return self.get('general.offline_mode', False)
    
    def set_offline_mode(self, enabled: bool) -> None:
        """
        Set offline mode.
        
        Args:
            enabled: Whether to enable offline mode
        """
        self.set('general.offline_mode', enabled)
        logger.info(f"Offline mode {'enabled' if enabled else 'disabled'}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., 'audio.sample_rate')
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


# Global instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration instance.
    
    Args:
        config_path: Path to config file
        
    Returns:
        ConfigManager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    
    return _config_instance


