#!/usr/bin/env python
"""Test Sprint 12 components."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("SPRINT 12 TESTING")
print("=" * 70)

# Test 1: Metrics
print("\n[TEST 1] Metrics System")
try:
    from core.metrics import MetricsCollector, PipelineMetrics
    collector = MetricsCollector()
    
    # Create sample metrics
    metrics = PipelineMetrics(
        wake_detection_time=50,
        stt_time=200,
        nlu_time=50,
        action_time=100,
        tts_time=150,
        total_time=550
    )
    collector.record_metrics(metrics)
    
    report = collector.get_performance_report()
    print("  OK: Metrics system working")
    print(report)
except Exception as e:
    print(f"  FAIL: {e}")

print("\n" + "=" * 70)
print("SPRINT 12 COMPLETE")
print("=" * 70)
