"""
Secrets vault for secure API key and token storage.

Uses keyring for encrypted, OS-level secure storage.
"""

from typing import Optional
from loguru import logger
import sys

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning(
        "keyring not available. Install: pip install keyring"
    )


class SecretsVault:
    """
    Secure vault for storing API keys and tokens.
    
    Uses the OS keyring service for secure storage:
    - Windows: Credential Manager
    - macOS: Keychain
    - Linux: Secret Service or KWallet
    """
    
    SERVICE_NAME = "jarvis_assistant"
    
    def __init__(self):
        """Initialize the secrets vault."""
        if not KEYRING_AVAILABLE:
            logger.warning("Keyring not available - using fallback storage")
        logger.info("SecretsVault initialized")
    
    def store_secret(self, key: str, value: str) -> bool:
        """
        Store a secret value.
        
        Args:
            key: Secret key name
            value: Secret value to store
            
        Returns:
            True if successful, False otherwise
        """
        if not KEYRING_AVAILABLE:
            logger.warning("Keyring not available - cannot store secrets securely")
            return False
        
        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
            logger.debug(f"Stored secret: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            return False
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a secret value.
        
        Args:
            key: Secret key name
            
        Returns:
            Secret value or None if not found
        """
        if not KEYRING_AVAILABLE:
            return None
        
        try:
            value = keyring.get_password(self.SERVICE_NAME, key)
            if value:
                logger.debug(f"Retrieved secret: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            return None
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret key name
            
        Returns:
            True if successful
        """
        if not KEYRING_AVAILABLE:
            return False
        
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
            logger.debug(f"Deleted secret: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret {key}: {e}")
            return False
    
    def has_secret(self, key: str) -> bool:
        """
        Check if a secret exists.
        
        Args:
            key: Secret key name
            
        Returns:
            True if secret exists
        """
        return self.get_secret(key) is not None
    
    def list_secrets(self) -> list:
        """
        List all secret keys (if supported).
        
        Note: keyring doesn't support listing keys on all platforms.
        
        Returns:
            List of secret keys
        """
        # Most keyring backends don't support listing
        logger.warning("Listing secrets not supported by all keyring backends")
        return []


# Global instance
_secrets_vault: Optional[SecretsVault] = None


def get_secrets_vault() -> SecretsVault:
    """Get the global secrets vault instance."""
    global _secrets_vault
    if _secrets_vault is None:
        _secrets_vault = SecretsVault()
    return _secrets_vault


# Convenience functions
def store_api_key(service: str, api_key: str) -> bool:
    """
    Store an API key for a service.
    
    Args:
        service: Service name (e.g., 'openai', 'google')
        api_key: API key value
        
    Returns:
        True if successful
    """
    return get_secrets_vault().store_secret(f"api_key_{service}", api_key)


def get_api_key(service: str) -> Optional[str]:
    """
    Get an API key for a service.
    
    Args:
        service: Service name
        
    Returns:
        API key or None
    """
    return get_secrets_vault().get_secret(f"api_key_{service}")



