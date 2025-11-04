"""
Metrics tracking and performance monitoring.

Tracks pipeline timings and performance metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import time
from loguru import logger


@dataclass
class PipelineMetrics:
    """
    Metrics for a single command pipeline execution.
    
    Attributes:
        wake_detection_time: Time to detect wake word (ms)
        stt_time: Time for speech-to-text (ms)
        nlu_time: Time for intent classification (ms)
        action_time: Time to execute skill (ms)
        tts_time: Time for text-to-speech (ms)
        total_time: Total pipeline time (ms)
        timestamp: When the command was executed
    """
    wake_detection_time: float = 0.0
    stt_time: float = 0.0
    nlu_time: float = 0.0
    action_time: float = 0.0
    tts_time: float = 0.0
    total_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """
    Collects and stores performance metrics.
    
    Features:
    - Track pipeline timings
    - Calculate averages
    - Generate performance reports
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[PipelineMetrics] = []
        self.max_metrics = 1000  # Keep last 1000 metrics
        
        logger.info("MetricsCollector initialized")
    
    def record_metrics(self, metrics: PipelineMetrics):
        """
        Record metrics for a command execution.
        
        Args:
            metrics: Pipeline metrics to record
        """
        self.metrics.append(metrics)
        
        # Trim if too many metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def get_average_times(self) -> Dict[str, float]:
        """
        Calculate average execution times.
        
        Returns:
            Dictionary with average times for each stage
        """
        if not self.metrics:
            return {}
        
        totals = {
            'wake': 0.0,
            'stt': 0.0,
            'nlu': 0.0,
            'action': 0.0,
            'tts': 0.0,
            'total': 0.0
        }
        
        for m in self.metrics:
            totals['wake'] += m.wake_detection_time
            totals['stt'] += m.stt_time
            totals['nlu'] += m.nlu_time
            totals['action'] += m.action_time
            totals['tts'] += m.tts_time
            totals['total'] += m.total_time
        
        count = len(self.metrics)
        return {k: v / count for k, v in totals.items()}
    
    def get_performance_report(self) -> str:
        """
        Generate a performance report.
        
        Returns:
            Formatted performance report string
        """
        if not self.metrics:
            return "No metrics collected yet."
        
        averages = self.get_average_times()
        
        report = "=" * 70 + "\n"
        report += "JARVIS PERFORMANCE REPORT\n"
        report += "=" * 70 + "\n\n"
        
        report += f"Total Commands: {len(self.metrics)}\n"
        report += f"Most Recent: {self.metrics[-1].timestamp}\n\n"
        
        report += "Average Pipeline Times:\n"
        report += "-" * 70 + "\n"
        report += f"  Wake Detection: {averages.get('wake', 0):.2f} ms\n"
        report += f"  Speech-to-Text: {averages.get('stt', 0):.2f} ms\n"
        report += f"  NLU Processing: {averages.get('nlu', 0):.2f} ms\n"
        report += f"  Skill Action:   {averages.get('action', 0):.2f} ms\n"
        report += f"  Text-to-Speech: {averages.get('tts', 0):.2f} ms\n"
        report += "-" * 70 + "\n"
        report += f"  Total Pipeline: {averages.get('total', 0):.2f} ms\n"
        report += "=" * 70 + "\n"
        
        return report
    
    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        logger.info("Metrics cleared")


# Global instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


class PerformanceTimer:
    """Context manager for timing code blocks."""
    
    def __init__(self, metric_name: str):
        """
        Initialize timer.
        
        Args:
            metric_name: Name of the metric being measured
        """
        self.metric_name = metric_name
        self.start_time: Optional[float] = None
        self.duration: float = 0.0
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing."""
        if self.start_time is not None:
            self.duration = (time.perf_counter() - self.start_time) * 1000  # Convert to ms
    
    def get_duration(self) -> float:
        """Get duration in milliseconds."""
        return self.duration



