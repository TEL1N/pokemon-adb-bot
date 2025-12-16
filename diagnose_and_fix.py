#!/usr/bin/env python3
"""
DIAGNOSTIC & FIX SCRIPT
Checks your emulator setup and helps recalibrate for multi-instance
"""

import subprocess
import json
import os
import sys
import time

ADB_PATH = r"C:\platform-tools\adb.exe"

# MuMu Player port patterns:
# - MuMu 12: 16384, 16416, 16448, 16480... (increments of 32)
# - MuMu classic: 7555, 7556, 7557...
# - Standard emulator: 5555, 5556...
# MuMu Player 12 uses ports starting at 16384, incrementing by 32
# Instance 1: 16384, Instance 2: 16416, Instance 3: 16448, etc.
MUMU12_BASE_PORT = 16384
MUMU12_PORT_INCREMENT = 32
MUMU12_MAX_INSTANCES = 10


def run_adb(args):
    """Run ADB command and return result"""
    cmd = [ADB_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def get_all_devices():
    """Get list of all connected devices"""
    result = run_adb(["devices"])
    
    devices = []
    lines = result.stdout.strip().split('\n')
    for line in lines[1:]:
        if '\tdevice' in line or '  device' in line:
            device_id = line.split()[0]
            devices.append(device_id)
    
    return devices


def verify_device_responsive(device_id):
    """Check if a device actually responds to commands"""
    try:
        result = subprocess.run(
            [ADB_PATH, "-s", device_id, "shell", "echo", "test"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.returncode == 0 and "test" in result.stdout
    except:
        return False


def cleanup_stale_connections():
    """Disconnect any stale/offline devices"""
    print("\n[CLEANUP] Removing stale connections...")
    
    result = run_adb(["devices"])
    lines = result.stdout.strip().split('\n')
    
    stale_count = 0
    for line in lines[1:]:
        if '\toffline' in line or '\tunauthorized' in line:
            device_id = line.split()[0]
            print(f"  Disconnecting stale: {device_id}")
            run_adb(["disconnect", device_id])
            stale_count += 1
    
    if stale_count == 0:
        print("  No stale connections found")
    else:
        print(f"  Removed {stale_count} stale connection(s)")


def auto_connect_all_instances():
    """
    Auto-discover and connect to all MuMu 12 instances
    Returns list of verified, responsive devices
    """
    # First, clean up any stale connections
    cleanup_stale_connections()
    
    print("\n[AUTO-CONNECT] Scanning for MuMu 12 instances...")
    print(f"  (Checking ports {MUMU12_BASE_PORT} to {MUMU12_BASE_PORT + MUMU12_PORT_INCREMENT * MUMU12_MAX_INSTANCES})")
    
    connected = []
    
    # Only scan MuMu 12 ports
    for i in range(MUMU12_MAX_INSTANCES):
        port = MUMU12_BASE_PORT + (i * MUMU12_PORT_INCREMENT)
        address = f"127.0.0.1:{port}"
        
        # Try to connect
        result = run_adb(["connect", address])
        output = result.stdout.lower()
        
        if "connected" in output and "cannot" not in output and "refused" not in output:
            # Verify it's actually responsive
            if verify_device_responsive(address):
                print(f"  ✓ Connected & verified: {address}")
                connected.append(address)
            else:
                print(f"  ✗ Connected but not responsive: {address}")
                run_adb(["disconnect", address])
        elif "already connected" in output:
            if verify_device_responsive(address):
                print(f"  ✓ Already connected & verified: {address}")
                connected.append(address)
            else:
                print(f"  ✗ Already connected but not responsive: {address}")
                run_adb(["disconnect", address])
        
        time.sleep(0.2)
    
    print(f"\n[AUTO-CONNECT] Complete!")
    print(f"  Verified devices: {len(connected)}")
    
    return connected

def get_device_info(device_id):
    """Get screen resolution and other info for a device"""
    # Get screen size
    result = subprocess.run(
        [ADB_PATH, "-s", device_id, "shell", "wm", "size"],
        capture_output=True,
        text=True
    )
    
    size = "Unknown"
    if "Physical size:" in result.stdout:
        size = result.stdout.strip().split(": ")[1]
    
    # Get density
    result = subprocess.run(
        [ADB_PATH, "-s", device_id, "shell", "wm", "density"],
        capture_output=True,
        text=True
    )
    
    density = "Unknown"
    if "Physical density:" in result.stdout:
        density = result.stdout.strip().split(": ")[1]
    
    return {"resolution": size, "density": density}

def check_config_files():
    """Check what config files exist"""
    configs = []
    
    # Check main config
    if os.path.exists("adb_config.json"):
        configs.append("adb_config.json")
    
    # Check device-specific configs
    for f in os.listdir("."):
        if f.startswith("adb_config_") and f.endswith(".json"):
            configs.append(f)
    
    return configs

def diagnose():
    """Run full diagnosis"""
    print("=" * 70)
    print("POKEMON TCG BOT - MULTI-INSTANCE DIAGNOSTIC")
    print("=" * 70)
    
    # Step 1: Auto-connect to all instances
    print("\n[1/5] AUTO-CONNECTING TO ALL MUMU INSTANCES...")
    devices = auto_connect_all_instances()
    
    if not devices:
        print("  ❌ NO DEVICES FOUND!")
        print("  Make sure:")
        print("    - MuMu Player is running")
        print("    - At least one instance is started")
        return False
    
    print(f"\n  ✓ Found {len(devices)} device(s):")
    device_info = {}
    for i, device in enumerate(devices, 1):
        info = get_device_info(device)
        device_info[device] = info
        print(f"    {i}. {device}")
        print(f"       Resolution: {info['resolution']}")
        print(f"       Density: {info['density']}")
    
    # Step 2: Check if all devices have same resolution
    print("\n[2/5] CHECKING RESOLUTION CONSISTENCY...")
    resolutions = set(info['resolution'] for info in device_info.values())
    
    if len(resolutions) == 1:
        print(f"  ✓ All devices have SAME resolution: {list(resolutions)[0]}")
        print("  → Single config file should work for all!")
        same_resolution = True
    else:
        print(f"  ⚠️ DIFFERENT RESOLUTIONS DETECTED:")
        for device, info in device_info.items():
            print(f"    {device}: {info['resolution']}")
        print("  → Each device needs its own config file!")
        same_resolution = False
    
    # Step 3: Check config files
    print("\n[3/5] CHECKING CONFIG FILES...")
    configs = check_config_files()
    
    if not configs:
        print("  ❌ NO CONFIG FILES FOUND!")
        print("  → Need to run calibration (test_02)")
    else:
        print(f"  Found {len(configs)} config file(s):")
        for config in configs:
            print(f"    - {config}")
            try:
                with open(config, 'r') as f:
                    data = json.load(f)
                    keys = list(data.keys())
                    print(f"      Keys: {', '.join(keys[:5])}...")
            except:
                print(f"      ⚠️ Could not read file")
    
    # Step 4: Recommendations
    print("\n[4/5] RECOMMENDATIONS...")
    print("-" * 70)
    
    if not configs:
        print("  1. Run calibration on ONE emulator first:")
        print("     python test_02_adb_calibration.py")
        print("")
        print("  2. Test the bot on that single emulator:")
        print("     python test_05_adb_full_workflow.py")
        print("")
        print("  3. Once working, test parallelization")
    
    elif not same_resolution:
        print("  ⚠️ CRITICAL: Your emulators have different resolutions!")
        print("")
        print("  OPTION A (Recommended): Make all emulators same resolution")
        print("    - In MuMu Player settings, set all to same resolution")
        print("    - Then recalibrate once")
        print("")
        print("  OPTION B: Use device-specific configs")
        print("    - Run calibration for each device separately")
        print("    - Use: python test_02_adb_calibration.py --device <device_id>")
    
    else:
        print("  ✓ Setup looks good!")
        print("")
        print("  If coordinates are off, try:")
        print("    1. Fresh calibration: python test_02_adb_calibration.py")
        print("    2. Test single instance first")
        print("    3. Then add more instances")
    
    # Step 5: Summary
    print("\n[5/5] SUMMARY...")
    print("-" * 70)
    print(f"  Devices connected: {len(devices)}")
    print(f"  Same resolution:   {'Yes' if same_resolution else 'No'}")
    print(f"  Config files:      {len(configs)}")
    
    print("\n" + "=" * 70)
    return True

def quick_test_single_device():
    """Quick test on first device"""
    print("\n" + "=" * 70)
    print("QUICK TEST: Single Device")
    print("=" * 70)
    
    devices = get_all_devices()
    if not devices:
        print("❌ No devices found")
        return
    
    device = devices[0]
    print(f"\nTesting device: {device}")
    
    # Take screenshot
    print("\n[1/3] Taking screenshot...")
    result = subprocess.run(
        [ADB_PATH, "-s", device, "exec-out", "screencap", "-p"],
        capture_output=True
    )
    
    if result.returncode == 0:
        with open("test_screenshot.png", "wb") as f:
            f.write(result.stdout)
        print("  ✓ Screenshot saved: test_screenshot.png")
    else:
        print(f"  ❌ Screenshot failed: {result.stderr}")
        return
    
    # Test tap
    print("\n[2/3] Testing tap at center...")
    info = get_device_info(device)
    if "x" in info['resolution']:
        w, h = map(int, info['resolution'].split('x'))
        center_x, center_y = w // 2, h // 2
        
        print(f"  Tapping at ({center_x}, {center_y})...")
        result = subprocess.run(
            [ADB_PATH, "-s", device, "shell", "input", "tap", str(center_x), str(center_y)],
            capture_output=True,
            text=True
        )
        print("  ✓ Tap command sent")
    
    # Test swipe
    print("\n[3/3] Testing swipe...")
    if "x" in info['resolution']:
        w, h = map(int, info['resolution'].split('x'))
        start_y = int(h * 0.7)
        end_y = int(h * 0.3)
        
        print(f"  Swiping from ({w//2}, {start_y}) to ({w//2}, {end_y})...")
        result = subprocess.run(
            [ADB_PATH, "-s", device, "shell", "input", "swipe", 
             str(w//2), str(start_y), str(w//2), str(end_y), "400"],
            capture_output=True,
            text=True
        )
        print("  ✓ Swipe command sent")
    
    print("\n✓ Quick test complete!")
    print("Check your emulator to see if tap and swipe worked.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test_single_device()
    else:
        diagnose()
        
        response = input("\nRun quick test on first device? (y/n): ").lower()
        if response == 'y':
            quick_test_single_device()