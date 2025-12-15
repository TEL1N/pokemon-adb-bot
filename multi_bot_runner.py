#!/usr/bin/env python3
import subprocess
import sys
import time
from adb_controller import ADBController

def main():
    print("Scanning for emulators...\n")
    
    # 1. Detect devices
    devices = ADBController.get_all_devices()
    
    if not devices:
        print("❌ No devices found!")
        print("  - Ensure emulators are running")
        print("  - Try: adb connect 127.0.0.1:7555")
        return

    print(f"✅ Found {len(devices)} device(s): {devices}")
    
    processes = []
    
    print("Starting parallel execution...")
    print("Press CTRL+C to stop all bots.\n")
    
    try:
        # 2. Launch a process for each device
        for device in devices:
            print(f"🚀 Launching process for {device}")
            
            # This calls: python bot_infinite_loop.py --device <device_id>
            # We use creationflags=subprocess.CREATE_NEW_CONSOLE only on Windows
            # to give each bot its own window (optional but helpful)
            cmd = [sys.executable, "bot_infinite_loop.py", "--device", device]
            
            # Using Popen to run in background
            p = subprocess.Popen(cmd)
            processes.append(p)
            time.sleep(2) # Stagger start times slightly
            
        # 3. Keep main script alive
        while True:
            time.sleep(1)
            # Check if any processes died
            for p in processes:
                if p.poll() is not None:
                    print("⚠️ One of the bot processes stopped unexpectedly.")
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()