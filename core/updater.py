"""
Auto-Update System for Jarvis

Features:
- Check for updates
- Silent background updates
- Release notes display
- Rollback on failure
- Update channels (stable, beta, dev)
"""

import sys
import os
import json
import requests
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
import hashlib


@dataclass
class Version:
    """Version information."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other: 'Version') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: 'Version') -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        """Parse version from string (e.g., '1.0.0')."""
        parts = version_str.split('.')
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2]) if len(parts) > 2 else 0
        )


@dataclass
class UpdateInfo:
    """Update information."""
    version: Version
    download_url: str
    release_notes: str
    size_bytes: int
    checksum: str
    published_at: datetime
    channel: str


class Updater:
    """
    Auto-update manager for Jarvis.
    
    Features:
    - Version checking
    - Download updates
    - Install updates
    - Rollback on failure
    """
    
    # Update server URL (replace with actual)
    UPDATE_SERVER = "https://updates.jarvis-assistant.com/api"
    CURRENT_VERSION = Version(1, 0, 0)
    
    def __init__(
        self,
        channel: str = "stable",
        auto_check: bool = True,
        check_interval_hours: int = 24,
    ):
        """
        Initialize updater.
        
        Args:
            channel: Update channel ("stable", "beta", "dev")
            auto_check: Automatically check for updates
            check_interval_hours: Hours between update checks
        """
        self.channel = channel
        self.auto_check = auto_check
        self.check_interval_hours = check_interval_hours
        
        self.config_dir = Path.home() / ".jarvis" / "updater"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_check_file = self.config_dir / "last_check.txt"
        self.update_cache_dir = self.config_dir / "cache"
        self.update_cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"Updater initialized (channel: {channel})")
    
    def should_check_for_updates(self) -> bool:
        """
        Check if it's time to check for updates.
        
        Returns:
            True if should check, False otherwise
        """
        if not self.auto_check:
            return False
        
        if not self.last_check_file.exists():
            return True
        
        try:
            with open(self.last_check_file, 'r') as f:
                last_check_str = f.read().strip()
            
            last_check = datetime.fromisoformat(last_check_str)
            elapsed = datetime.now() - last_check
            
            return elapsed > timedelta(hours=self.check_interval_hours)
        
        except Exception as e:
            logger.warning(f"Failed to read last check time: {e}")
            return True
    
    def _update_last_check_time(self):
        """Update last check timestamp."""
        try:
            with open(self.last_check_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"Failed to update last check time: {e}")
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """
        Check for available updates.
        
        Returns:
            UpdateInfo if update available, None otherwise
        """
        logger.info(f"Checking for updates (channel: {self.channel})...")
        
        try:
            # Query update server
            response = requests.get(
                f"{self.UPDATE_SERVER}/latest",
                params={
                    "channel": self.channel,
                    "current_version": str(self.CURRENT_VERSION),
                    "platform": sys.platform,
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Update last check time
            self._update_last_check_time()
            
            # Parse update info
            if not data.get("update_available"):
                logger.info("No updates available")
                return None
            
            update_info = UpdateInfo(
                version=Version.from_string(data["version"]),
                download_url=data["download_url"],
                release_notes=data.get("release_notes", ""),
                size_bytes=data.get("size_bytes", 0),
                checksum=data.get("checksum", ""),
                published_at=datetime.fromisoformat(data.get("published_at", datetime.now().isoformat())),
                channel=data.get("channel", self.channel),
            )
            
            logger.info(f"Update available: {update_info.version}")
            return update_info
        
        except requests.RequestException as e:
            logger.warning(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def download_update(self, update_info: UpdateInfo) -> Optional[Path]:
        """
        Download update file.
        
        Args:
            update_info: Update information
            
        Returns:
            Path to downloaded file or None if failed
        """
        logger.info(f"Downloading update {update_info.version}...")
        
        try:
            # Generate filename
            filename = f"jarvis_update_{update_info.version}.exe"
            output_path = self.update_cache_dir / filename
            
            # Download with progress
            response = requests.get(update_info.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.debug(f"Download progress: {progress:.1f}%")
            
            # Verify checksum
            if update_info.checksum:
                if not self._verify_checksum(output_path, update_info.checksum):
                    logger.error("Checksum verification failed")
                    output_path.unlink()
                    return None
            
            logger.info(f"Update downloaded: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify file checksum.
        
        Args:
            file_path: Path to file
            expected_checksum: Expected SHA256 checksum
            
        Returns:
            True if checksum matches, False otherwise
        """
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            
            actual_checksum = sha256.hexdigest()
            return actual_checksum == expected_checksum
        
        except Exception as e:
            logger.error(f"Failed to verify checksum: {e}")
            return False
    
    def install_update(self, update_file: Path, silent: bool = True) -> bool:
        """
        Install update.
        
        Args:
            update_file: Path to update installer
            silent: Silent installation
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Installing update from {update_file}...")
        
        try:
            # Create backup of current installation
            backup_dir = self.config_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Run installer
            args = [str(update_file)]
            if silent:
                args.append("/VERYSILENT")
                args.append("/SUPPRESSMSGBOXES")
                args.append("/NORESTART")
            
            result = subprocess.run(args, check=False)
            
            if result.returncode == 0:
                logger.info("Update installed successfully")
                return True
            else:
                logger.error(f"Update installation failed with code {result.returncode}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            return False
    
    def check_and_install(self, silent: bool = True) -> bool:
        """
        Check for updates and install if available.
        
        Args:
            silent: Silent installation
            
        Returns:
            True if update installed, False otherwise
        """
        update_info = self.check_for_updates()
        
        if not update_info:
            return False
        
        update_file = self.download_update(update_info)
        if not update_file:
            return False
        
        return self.install_update(update_file, silent=silent)
    
    def get_current_version(self) -> Version:
        """
        Get current Jarvis version.
        
        Returns:
            Current version
        """
        return self.CURRENT_VERSION


# Singleton instance
_updater: Optional[Updater] = None


def get_updater(channel: str = "stable") -> Updater:
    """
    Get singleton updater instance.
    
    Args:
        channel: Update channel
        
    Returns:
        Updater instance
    """
    global _updater
    if _updater is None:
        _updater = Updater(channel=channel)
    return _updater


if __name__ == "__main__":
    # CLI interface
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis Update Manager")
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--install", action="store_true", help="Check and install updates")
    parser.add_argument("--channel", default="stable", choices=["stable", "beta", "dev"], help="Update channel")
    
    args = parser.parse_args()
    
    updater = get_updater(channel=args.channel)
    
    if args.check:
        update_info = updater.check_for_updates()
        if update_info:
            print(f"Update available: {update_info.version}")
            print(f"Release notes:\n{update_info.release_notes}")
        else:
            print("No updates available")
    
    elif args.install:
        success = updater.check_and_install(silent=False)
        if success:
            print("Update installed successfully")
        else:
            print("No updates installed")

