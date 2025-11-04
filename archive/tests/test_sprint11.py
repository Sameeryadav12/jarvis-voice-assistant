#!/usr/bin/env python
"""Test Sprint 11 components."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("SPRINT 11 TESTING")
print("=" * 70)

# Test 1: Permissions
print("\n[TEST 1] Permissions System")
try:
    from core.permissions import PermissionManager, PermissionScope
    pm = PermissionManager()
    print("  OK: Permissions system loaded")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Secrets Vault
print("\n[TEST 2] Secrets Vault")
try:
    from core.secrets import SecretsVault
    vault = SecretsVault()
    print("  OK: Secrets vault loaded")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Offline Mode
print("\n[TEST 3] Offline Mode")
try:
    from core.config.config_manager import ConfigManager
    config = ConfigManager()
    is_offline = config.is_offline_mode()
    print(f"  OK: Offline mode = {is_offline}")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Crash Reporter
print("\n[TEST 4] Crash Reporter")
try:
    from core.reporter import CrashReporter
    reporter = CrashReporter()
    print("  OK: Crash reporter loaded")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n" + "=" * 70)
print("SPRINT 11 TESTS COMPLETE")
print("=" * 70)



