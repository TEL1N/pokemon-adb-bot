#!/usr/bin/env python3
"""
ADB Controller - Replaces PyAutoGUI for emulator control
Supports auto-detection and multiple devices
"""

import subprocess
import cv2
import numpy as np
import time
from PIL import Image
import io


class ADBController:
    # Full path to adb.exe
    ADB_PATH = r"C:\platform-tools\adb.exe"
    
    @staticmethod
    def get_all_devices():
        """Get list of all connected devices"""
        result = subprocess.run(
            [ADBController.ADB_PATH, "devices"],
            capture_output=True,
            text=True
        )
        
        devices = []
        lines = result.stdout.strip().split('\n')
        for line in lines[1:]:  # Skip "List of devices attached"
            if '\tdevice' in line or '  device' in line:
                device_id = line.split()[0]
                devices.append(device_id)
        
        return devices
    
    @staticmethod
    def get_connected_device():
        """Automatically find the first connected device"""
        devices = ADBController.get_all_devices()
        
        if len(devices) == 0:
            return None
        
        return devices[0]
    
    @staticmethod
    def select_device():
        """Interactive device selection when multiple devices connected"""
        devices = ADBController.get_all_devices()
        
        if len(devices) == 0:
            print("✗ No devices found!")
            print("Make sure:")
            print("  1. Mumuplayer is running")
            print("  2. Run: adb connect 127.0.0.1:7555")
            return None
        
        if len(devices) == 1:
            print(f"✓ Found 1 device: {devices[0]}")
            return devices[0]
        
        # Multiple devices - let user choose
        print(f"\n✓ Found {len(devices)} devices:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
        
        while True:
            try:
                choice = input(f"\nSelect device (1-{len(devices)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(devices):
                    return devices[index]
                else:
                    print(f"Invalid choice. Enter 1-{len(devices)}")
            except ValueError:
                print("Invalid input. Enter a number.")
    
    def __init__(self, device_id=None):
        """
        Initialize ADB controller for a specific device
        
        Args:
            device_id: ADB device identifier
                      - If None: auto-detect first device
                      - If "select": interactive selection for multiple devices
                      - If specific ID: use that device
        """
        if device_id is None:
            # Auto-detect first device
            device_id = self.get_connected_device()
            if device_id is None:
                raise ConnectionError(
                    "No devices found!\n"
                    "Steps to connect:\n"
                    "  1. Open Mumuplayer\n"
                    "  2. Run: adb connect 127.0.0.1:7555\n"
                    "  3. Run: adb devices (to verify)"
                )
            print(f"✓ Auto-detected device: {device_id}")
        
        elif device_id == "select":
            # Interactive selection
            device_id = self.select_device()
            if device_id is None:
                raise ConnectionError("No device selected")
        
        self.device = device_id
        print(f"✓ ADB Controller initialized for device: {self.device}")
        
        # Verify device is connected
        if not self._is_device_connected():
            raise ConnectionError(
                f"Device {self.device} not found!\n"
                f"Run 'adb devices' to check connection."
            )
    
    def _is_device_connected(self):
        """Check if device is connected"""
        devices = self.get_all_devices()
        return self.device in devices
    
    def _run_adb_command(self, command):
        """Execute ADB command and return output"""
        full_command = [self.ADB_PATH, "-s", self.device] + command
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True
        )
        return result
    
    # ==================== INPUT CONTROL ====================
    
    def tap(self, x, y, delay=0.3):
        """
        Tap at coordinates (x, y)
        
        Args:
            x: X coordinate
            y: Y coordinate
            delay: Delay after tap (seconds)
        """
        print(f"  [ADB] Tap at ({x}, {y})")
        self._run_adb_command(["shell", "input", "tap", str(x), str(y)])
        time.sleep(delay)
    
    def swipe(self, x1, y1, x2, y2, duration=400, delay=0.5):
        """
        Swipe from (x1, y1) to (x2, y2)
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in milliseconds
            delay: Delay after swipe (seconds)
        """
        print(f"  [ADB] Swipe from ({x1}, {y1}) to ({x2}, {y2})")
        self._run_adb_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
        time.sleep(delay)
    
    def swipe_with_hold(self, x1, y1, x2, y2, duration=400, hold_time=1000, delay=0.5):
        """
        Swipe with hold at end point to prevent flick
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in milliseconds
            hold_time: Time to hold at end before release (milliseconds)
            delay: Delay after complete gesture (seconds)
        """
        print(f"  [ADB] Swipe with hold from ({x1}, {y1}) to ({x2}, {y2})")
        
        # Total duration includes both swipe and hold
        total_duration = duration + hold_time
        
        self._run_adb_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(total_duration)
        ])
        
        time.sleep(delay)
    
    def press_key(self, keycode, delay=0.3):
        """
        Press a key using Android keycode
        
        Common keycodes:
            KEYCODE_BACK = 4
            KEYCODE_HOME = 3
            KEYCODE_MENU = 82
            KEYCODE_ENTER = 66
        
        Args:
            keycode: Android keycode number
            delay: Delay after keypress (seconds)
        """
        print(f"  [ADB] Press key {keycode}")
        self._run_adb_command(["shell", "input", "keyevent", str(keycode)])
        time.sleep(delay)
    
    def press_back(self, delay=0.3):
        """Press Android BACK button"""
        self.press_key(4, delay)
    
    def press_home(self, delay=0.3):
        """Press Android HOME button"""
        self.press_key(3, delay)
    
    # ==================== SCREEN CAPTURE ====================
    
    def screenshot_raw(self):
        """
        Take screenshot and return as PIL Image
        
        Returns:
            PIL Image object
        """
        result = subprocess.run(
            [self.ADB_PATH, "-s", self.device, "exec-out", "screencap", "-p"],
            capture_output=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Screenshot failed: {result.stderr}")
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(result.stdout))
        return image
    
    def screenshot_cv(self):
        """
        Take screenshot and return as OpenCV image (BGR format)
        
        Returns:
            numpy array (OpenCV BGR image)
        """
        pil_image = self.screenshot_raw()
        
        # Convert PIL to OpenCV format
        # PIL is RGB, OpenCV uses BGR
        rgb_array = np.array(pil_image)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        
        return bgr_array
    
    def screenshot_region(self, x, y, width, height):
        """
        Take screenshot and crop to specific region
        
        Args:
            x, y: Top-left corner
            width, height: Region size
        
        Returns:
            OpenCV image (BGR) of the cropped region
        """
        full_screenshot = self.screenshot_cv()
        
        # Crop the region
        cropped = full_screenshot[y:y+height, x:x+width]
        
        return cropped
    
    def save_screenshot(self, filename="screenshot.png"):
        """
        Save screenshot to file
        
        Args:
            filename: Output filename
        """
        image = self.screenshot_raw()
        image.save(filename)
        print(f"✓ Screenshot saved: {filename}")
    
    # ==================== UTILITY ====================
    
    def get_screen_size(self):
        """
        Get emulator screen resolution
        
        Returns:
            tuple: (width, height)
        """
        result = self._run_adb_command(["shell", "wm", "size"])
        # Output format: "Physical size: 1080x1920"
        size_line = result.stdout.strip()
        
        if "Physical size:" in size_line:
            dimensions = size_line.split(": ")[1]
            width, height = map(int, dimensions.split("x"))
            return (width, height)
        else:
            # Fallback: take screenshot and get dimensions
            img = self.screenshot_cv()
            height, width = img.shape[:2]
            return (width, height)
    
    def wait(self, seconds):
        """Simple wait/sleep"""
        print(f"  [Wait] {seconds}s")
        time.sleep(seconds)


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    # Test auto-detection
    print("\n=== Testing Auto-Detection ===")
    
    try:
        controller = ADBController()  # Auto-detect first device
        
        # Get screen size
        width, height = controller.get_screen_size()
        print(f"Screen size: {width}x{height}")
        
        # Take screenshot
        controller.save_screenshot("test_adb.png")
        
        print("\n✓ Auto-detection test complete!")
        
    except ConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
    
    # Test multi-device selection
    print("\n=== Available Devices ===")
    devices = ADBController.get_all_devices()
    if devices:
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
    else:
        print("  No devices found")