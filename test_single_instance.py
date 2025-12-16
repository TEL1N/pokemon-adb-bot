#!/usr/bin/env python3
"""
SINGLE INSTANCE TEST
Tests the full workflow on ONE emulator before parallelization
"""

import json
import time
import sys
import os

# Inline ADB controller to avoid import issues
import subprocess
import numpy as np
from PIL import Image
import cv2
import io


class ADBController:
    ADB_PATH = r"C:\platform-tools\adb.exe"
    
    @staticmethod
    def get_all_devices():
        result = subprocess.run(
            [ADBController.ADB_PATH, "devices"],
            capture_output=True,
            text=True
        )
        devices = []
        lines = result.stdout.strip().split('\n')
        for line in lines[1:]:
            if '\tdevice' in line or '  device' in line:
                device_id = line.split()[0]
                devices.append(device_id)
        return devices
    
    def __init__(self, device_id=None):
        if device_id is None:
            devices = self.get_all_devices()
            if not devices:
                raise ConnectionError("No devices found!")
            device_id = devices[0]
            print(f"✓ Auto-detected device: {device_id}")
        self.device = device_id
    
    def _run_adb_command(self, command):
        full_command = [self.ADB_PATH, "-s", self.device] + command
        return subprocess.run(full_command, capture_output=True, text=True)
    
    def tap(self, x, y, delay=0.3):
        self._run_adb_command(["shell", "input", "tap", str(x), str(y)])
        time.sleep(delay)
    
    def swipe(self, x1, y1, x2, y2, duration=400, delay=0.5):
        self._run_adb_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
        time.sleep(delay)
    
    def swipe_with_hold(self, x1, y1, x2, y2, duration=400, hold_time=1000, delay=0.5):
        total_duration = duration + hold_time
        self._run_adb_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(total_duration)
        ])
        time.sleep(delay)
    
    def press_back(self, delay=0.3):
        self._run_adb_command(["shell", "input", "keyevent", "4"])
        time.sleep(delay)
    
    def press_home(self, delay=0.3):
        self._run_adb_command(["shell", "input", "keyevent", "3"])
        time.sleep(delay)
    
    def screenshot_cv(self):
        result = subprocess.run(
            [self.ADB_PATH, "-s", self.device, "exec-out", "screencap", "-p"],
            capture_output=True
        )
        image = Image.open(io.BytesIO(result.stdout))
        rgb_array = np.array(image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)


def load_config(device_id=None):
    """Load config file (device-specific or shared)"""
    # Try device-specific first
    if device_id:
        sanitized = device_id.replace(":", "_").replace(".", "_")
        device_config = f"adb_config_{sanitized}.json"
        if os.path.exists(device_config):
            print(f"✓ Loading device-specific config: {device_config}")
            with open(device_config, 'r') as f:
                return json.load(f)
    
    # Fall back to shared config
    if os.path.exists("adb_config.json"):
        print("✓ Loading shared config: adb_config.json")
        with open("adb_config.json", 'r') as f:
            return json.load(f)
    
    print("❌ No config file found!")
    return None


def test_navigation(controller, config):
    """Test basic navigation"""
    print("\n" + "=" * 60)
    print("TEST: Basic Navigation")
    print("=" * 60)
    
    # Test Battles tab
    if "battles_tab" in config:
        print("\n[1/5] Testing Battles tab...")
        pos = tuple(config["battles_tab"])
        print(f"  Tapping at {pos}")
        controller.tap(*pos)
        time.sleep(2)
        
        response = input("  Did it open Battles screen? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Battles tab failed!")
            return False
        print("  ✓ Battles tab works")
    
    # Test Solo Battle
    if "solo_battle_button" in config:
        print("\n[2/5] Testing Solo Battle button...")
        pos = tuple(config["solo_battle_button"])
        print(f"  Tapping at {pos}")
        controller.tap(*pos)
        time.sleep(2)
        
        response = input("  Did it open Solo Battle? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Solo Battle button failed!")
            return False
        print("  ✓ Solo Battle button works")
    
    # Test BEGINNER (NO scroll needed - visible immediately)
    if "difficulty_buttons" in config and "beginner" in config["difficulty_buttons"]:
        print("\n[3/5] Testing BEGINNER button (no scroll needed)...")
        pos = tuple(config["difficulty_buttons"]["beginner"])
        print(f"  Tapping at {pos}")
        controller.tap(*pos)
        time.sleep(2)
        
        response = input("  Did it enter Beginner difficulty? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Beginner button failed!")
            return False
        print("  ✓ Beginner button works")
        
        # Go back to test other difficulties
        print("  Pressing BACK to return...")
        controller.press_back(delay=2)
    
    # Test difficulty scroll (needed for Intermediate/Advanced/Expert)
    if "difficulty_scroll" in config:
        print("\n[4/5] Testing difficulty scroll (needed for Int/Adv/Exp)...")
        scroll = config["difficulty_scroll"]
        start = tuple(scroll["start"])
        end = tuple(scroll["end"])
        
        print(f"  Swiping from {start} to {end} (2 times)")
        controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1)
        controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1)
        
        response = input("  Are Intermediate/Advanced/Expert visible now? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Difficulty scroll failed!")
            return False
        print("  ✓ Difficulty scroll works")
    
    # Test INTERMEDIATE (after scroll)
    if "difficulty_buttons" in config and "intermediate" in config["difficulty_buttons"]:
        print("\n[5/5] Testing INTERMEDIATE button (after scroll)...")
        pos = tuple(config["difficulty_buttons"]["intermediate"])
        print(f"  Tapping at {pos}")
        controller.tap(*pos)
        time.sleep(2)
        
        response = input("  Did it enter Intermediate difficulty? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Intermediate button failed!")
            return False
        print("  ✓ Intermediate button works")
    
    print("\n✓ All navigation tests passed!")
    return True


def test_expansions(controller, config):
    """Test expansion navigation"""
    print("\n" + "=" * 60)
    print("TEST: Expansion Navigation")
    print("=" * 60)
    
    # Test Expansions button
    if "expansions_button" in config:
        print("\n[1/4] Testing Expansions button...")
        pos = tuple(config["expansions_button"])
        print(f"  Tapping at {pos}")
        controller.tap(*pos)
        time.sleep(2)
        
        response = input("  Did Expansions menu open? (y/n): ").lower()
        if response != 'y':
            print("  ❌ Expansions button failed!")
            return False
        print("  ✓ Expansions button works")
    
    # Test series buttons
    if "series_buttons" in config:
        series = config["series_buttons"]
        
        if "B" in series:
            print("\n[2/4] Testing B-series button...")
            pos = tuple(series["B"])
            print(f"  Tapping at {pos}")
            controller.tap(*pos)
            time.sleep(1.5)
            
            response = input("  Did it switch to B-series? (y/n): ").lower()
            if response != 'y':
                print("  ❌ B-series button failed!")
                return False
            print("  ✓ B-series button works")
        
        if "A" in series:
            print("\n[3/4] Testing A-series button...")
            pos = tuple(series["A"])
            print(f"  Tapping at {pos}")
            controller.tap(*pos)
            time.sleep(1.5)
            
            response = input("  Did it switch to A-series? (y/n): ").lower()
            if response != 'y':
                print("  ❌ A-series button failed!")
                return False
            print("  ✓ A-series button works")
    
    # Test expansion scroll
    if "expansion_scroll" in config:
        print("\n[4/4] Testing expansion scroll...")
        scroll = config["expansion_scroll"]
        start = tuple(scroll["start"])
        end = tuple(scroll["end"])
        
        print(f"  Swiping from {start} to {end}")
        controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1.2)
        
        response = input("  Did it scroll ONE expansion? (y/n): ").lower()
        if response != 'y':
            print("  ⚠️ Expansion scroll may need adjustment")
        else:
            print("  ✓ Expansion scroll works")
    
    print("\n✓ Expansion tests complete!")
    return True


def test_reward_detection(controller, config):
    """Test reward icon detection"""
    print("\n" + "=" * 60)
    print("TEST: Reward Detection")
    print("=" * 60)
    
    if "reward_detection_region" not in config:
        print("❌ No reward detection region configured!")
        return False
    
    region = tuple(config["reward_detection_region"])
    x, y, w, h = region
    
    print(f"\nReward region: x={x}, y={y}, w={w}, h={h}")
    print("\nMake sure you're viewing battles with REWARD ICONS visible")
    
    input("\nPress ENTER to take screenshot and analyze...")
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    # Crop to region
    cropped = screenshot[y:y+h, x:x+w]
    
    # Convert to HSV
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    
    # Color ranges for rewards
    color_ranges = [
        ([80, 100, 150], [130, 255, 255]),   # Cyan/Blue
        ([130, 100, 150], [170, 255, 255]),  # Purple
        ([15, 100, 150], [45, 255, 255]),    # Yellow
        ([0, 120, 180], [180, 255, 255])     # Bright colors
    ]
    
    combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in color_ranges:
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    
    # Find contours
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"\nFound {len(contours)} potential objects")
    
    # Filter by size
    valid_count = 0
    result = screenshot.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 150 < area < 3000:
            valid_count += 1
            bx, by, bw, bh = cv2.boundingRect(contour)
            cv2.rectangle(result, (x+bx, y+by), (x+bx+bw, y+by+bh), (0, 255, 0), 2)
    
    print(f"Valid reward icons detected: {valid_count}")
    
    # Show result
    cv2.imshow("Detection Result", result)
    print("\nGreen boxes = detected rewards")
    print("Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    response = input("\nDid it correctly detect reward icons? (y/n): ").lower()
    if response == 'y':
        print("✓ Reward detection works!")
        return True
    else:
        print("⚠️ Reward detection may need adjustment")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("SINGLE INSTANCE TEST SUITE")
    print("=" * 60)
    
    # Get device
    devices = ADBController.get_all_devices()
    if not devices:
        print("❌ No devices found!")
        return
    
    print(f"\nFound {len(devices)} device(s):")
    for i, d in enumerate(devices, 1):
        print(f"  {i}. {d}")
    
    if len(devices) > 1:
        choice = input(f"\nSelect device (1-{len(devices)}): ").strip()
        device_id = devices[int(choice) - 1]
    else:
        device_id = devices[0]
    
    print(f"\n✓ Using device: {device_id}")
    
    # Load config
    config = load_config(device_id)
    if not config:
        print("\n❌ Cannot proceed without config!")
        print("Run: python calibrate_improved.py")
        return
    
    print(f"\nConfig has {len(config)} items:")
    for key in config:
        print(f"  ✓ {key}")
    
    # Create controller
    controller = ADBController(device_id)
    
    # Run tests
    print("\n" + "=" * 60)
    print("TESTS MENU")
    print("=" * 60)
    print("  1. Test Navigation (tabs, buttons)")
    print("  2. Test Expansions (menu, series, scroll)")
    print("  3. Test Reward Detection")
    print("  4. Run ALL tests")
    
    choice = input("\nSelect (1-4): ").strip()
    
    if choice == "1":
        test_navigation(controller, config)
    elif choice == "2":
        test_expansions(controller, config)
    elif choice == "3":
        test_reward_detection(controller, config)
    elif choice == "4":
        print("\n--- Running ALL Tests ---")
        
        input("\nSetup: Make sure you're at the MAIN MENU. Press ENTER...")
        
        nav_ok = test_navigation(controller, config)
        if nav_ok:
            exp_ok = test_expansions(controller, config)
            if exp_ok:
                test_reward_detection(controller, config)
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    run_all_tests()