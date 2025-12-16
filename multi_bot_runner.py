#!/usr/bin/env python3
"""
MULTI-BOT RUNNER
Auto-discovers all MuMu 12 instances and launches a bot for each
Each bot runs in its own process with its own progress tracking
"""

import subprocess
import sys
import time
import os

# MuMu 12 port configuration
MUMU12_BASE_PORT = 16384
MUMU12_PORT_INCREMENT = 32
MUMU12_MAX_INSTANCES = 10
ADB_PATH = r"C:\platform-tools\adb.exe"


def run_adb(args):
    """Run ADB command"""
    cmd = [ADB_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def verify_device_responsive(device_id):
    """Check if device actually responds"""
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


def auto_connect_mumu_instances():
    """
    Auto-discover and connect to all MuMu 12 instances
    Returns list of verified, responsive device IDs
    """
    print("=" * 60)
    print("AUTO-CONNECTING TO MUMU 12 INSTANCES")
    print("=" * 60)
    
    connected = []
    
    for i in range(MUMU12_MAX_INSTANCES):
        port = MUMU12_BASE_PORT + (i * MUMU12_PORT_INCREMENT)
        address = f"127.0.0.1:{port}"
        
        # Try to connect
        result = run_adb(["connect", address])
        output = result.stdout.lower()
        
        if "connected" in output and "cannot" not in output and "refused" not in output:
            if verify_device_responsive(address):
                print(f"  ✓ Connected & verified: {address}")
                connected.append(address)
        elif "already connected" in output:
            if verify_device_responsive(address):
                print(f"  ✓ Already connected: {address}")
                connected.append(address)
        
        time.sleep(0.2)
    
    print(f"\n✓ Found {len(connected)} active emulator(s)")
    return connected


def main():
    print("\n" + "=" * 60)
    print("POKEMON TCG POCKET - MULTI-BOT RUNNER")
    print("=" * 60)
    
    # Step 1: Find all emulators
    print("\n[Step 1] Scanning for emulators...")
    devices = auto_connect_mumu_instances()
    
    if not devices:
        print("\n❌ No emulators found!")
        print("Make sure:")
        print("  - MuMu Player 12 is running")
        print("  - At least one instance is started")
        return
    
    print(f"\n[Step 2] Found {len(devices)} emulator(s):")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # Confirm before launching
    print(f"\n[Step 3] Ready to launch {len(devices)} bot(s)")
    response = input("Start all bots? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Cancelled.")
        return
    
    # Step 4: Launch bot processes
    print(f"\n[Step 4] Launching {len(devices)} bot process(es)...")
    print("-" * 60)
    
    processes = []
    
    for i, device in enumerate(devices):
        print(f"  🚀 Launching bot for {device}...")
        
        # Launch each bot in its own process
        # CREATE_NEW_CONSOLE gives each bot its own window on Windows
        cmd = [sys.executable, "bot_infinite_loop.py", "--device", device]
        
        try:
            # On Windows, use CREATE_NEW_CONSOLE for separate windows
            if sys.platform == "win32":
                p = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # On Linux/Mac, just run in background
                p = subprocess.Popen(cmd)
            
            processes.append({"device": device, "process": p})
            print(f"  ✓ Bot started for {device} (PID: {p.pid})")
            
            # Stagger starts to avoid all bots hitting same resources
            if i < len(devices) - 1:
                print(f"  Waiting 5 seconds before next bot...")
                time.sleep(5)
                
        except Exception as e:
            print(f"  ❌ Failed to start bot for {device}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✓ {len(processes)} BOT(S) RUNNING")
    print("=" * 60)
    print("\nEach bot has its own console window.")
    print("Press CTRL+C here to stop the monitor (bots will keep running)")
    print("Close individual console windows to stop specific bots")
    print("-" * 60)
    
    # Monitor loop
    try:
        while True:
            time.sleep(10)
            
            # Check which processes are still running
            running = []
            for p_info in processes:
                if p_info["process"].poll() is None:
                    running.append(p_info["device"])
                else:
                    print(f"⚠️ Bot for {p_info['device']} has stopped")
            
            if not running:
                print("\n❌ All bots have stopped!")
                break
                
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("MONITOR STOPPED")
        print("=" * 60)
        print("Note: Bot windows are still running independently.")
        print("Close each bot's console window to stop it.")


if __name__ == "__main__":
    main()