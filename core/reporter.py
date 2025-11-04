"""
Crash reporter and error logging.

Collects crash information and provides reporting capabilities.
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger


class CrashReporter:
    """
    Handles crash reporting and error logging.
    
    Features:
    - Automatic crash detection
    - Error stack traces
    - Configuration state capture
    - Manual report generation
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize crash reporter.
        
        Args:
            log_dir: Directory for crash logs
        """
        if log_dir is None:
            log_dir = Path.home() / ".jarvis" / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_dir
        
        # Setup crash handler
        self._setup_crash_handler()
        
        logger.info("CrashReporter initialized")
    
    def _setup_crash_handler(self):
        """Setup global crash handler."""
        def crash_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger.error(
                f"Uncaught exception: {exc_type.__name__}: {exc_value}",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            
            self.report_crash(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = crash_handler
    
    def report_crash(
        self,
        exc_type: type,
        exc_value: Exception,
        exc_traceback: Any
    ) -> Path:
        """
        Report a crash with full details.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
            
        Returns:
            Path to crash log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_log = self.log_dir / f"crash_{timestamp}.log"
        
        try:
            with open(crash_log, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("JARVIS CRASH REPORT\n")
                f.write("=" * 70 + "\n                    \n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"Exception: {exc_type.__name__}\n")
                f.write(f"Message: {str(exc_value)}\n\n")
                
                f.write("Traceback:\n")
                f.write("-" * 70 + "\n")
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=f
                )
                
                f.write("\n" + "=" * 70 + "\n")
            
            logger.info(f"Crash report saved: {crash_log}")
            return crash_log
        
        except Exception as e:
            logger.error(f"Failed to save crash report: {e}")
            raise
    
    def get_recent_crashes(self, count: int = 5) -> list:
        """
        Get recent crash logs.
        
        Args:
            count: Number of recent crashes to return
            
        Returns:
            List of crash log paths
        """
        crash_logs = sorted(self.log_dir.glob("crash_*.log"), reverse=True)
        return list(crash_logs[:count])


# Global instance
_reporter: Optional[CrashReporter] = None


def get_reporter() -> CrashReporter:
    """Get the global crash reporter instance."""
    global _reporter
    if _reporter is None:
        _reporter = CrashReporter()
    return _reporter



