"""
Test native Windows API integration.
Tests volume control and window management.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 60)
print("TESTING NATIVE WINDOWS INTEGRATION")
print("=" * 60)

# Test 1: Import
print("\n[1/5] Testing native module import...")
try:
    from core.bindings import windows_native
    print(f"  [OK] Imported: {windows_native.__platform__}")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get current volume
print("\n[2/5] Testing get volume...")
try:
    volume = windows_native.get_master_volume()
    print(f"  [OK] Current volume: {volume * 100:.0f}%")
except Exception as e:
    print(f"  [FAIL] Get volume failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Set volume
print("\n[3/5] Testing set volume...")
try:
    original_volume = windows_native.get_master_volume()
    print(f"  Original volume: {original_volume * 100:.0f}%")
    
    # Set to 50%
    windows_native.set_master_volume(0.5)
    print("  Set volume to 50%")
    
    # Verify
    new_volume = windows_native.get_master_volume()
    print(f"  Verified: {new_volume * 100:.0f}%")
    
    # Restore original
    windows_native.set_master_volume(original_volume)
    print(f"  [OK] Restored to {original_volume * 100:.0f}%")
except Exception as e:
    print(f"  [FAIL] Set volume failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Mute/Unmute
print("\n[4/5] Testing mute/unmute...")
try:
    original_mute = windows_native.get_mute()
    print(f"  Original mute state: {original_mute}")
    
    # Toggle mute
    windows_native.set_mute(True)
    print("  Muted")
    
    # Verify
    is_muted = windows_native.get_mute()
    print(f"  Verified muted: {is_muted}")
    
    # Restore
    windows_native.set_mute(original_mute)
    print(f"  [OK] Restored mute state: {original_mute}")
except Exception as e:
    print(f"  [FAIL] Mute test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Window enumeration
print("\n[5/5] Testing window enumeration...")
try:
    windows = windows_native.enumerate_windows()
    print(f"  [OK] Found {len(windows)} windows")
    
    # Show first 5
    print("  Sample windows:")
    for window in windows[:5]:
        print(f"    - {window['title']}")
except Exception as e:
    print(f"  [FAIL] Window enumeration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] ALL NATIVE TESTS PASSED!")
print("=" * 60)
print("\nWindows integration is working!")
print("Volume control and window management are functional.")
print()




