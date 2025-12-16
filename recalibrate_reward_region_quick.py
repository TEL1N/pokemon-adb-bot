#!/usr/bin/env python3
"""
QUICK RECALIBRATE: Reward Detection Region ONLY
"""

import json
import cv2
import subprocess
import numpy as np
from PIL import Image
import io
import time

ADB_PATH = r"C:\platform-tools\adb.exe"


def get_devices():
    """Get connected devices"""
    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    devices = []
    for line in result.stdout.strip().split('\n')[1:]:
        if '\tdevice' in line:
            devices.append(line.split()[0])
    return devices


def screenshot(device_id):
    """Take screenshot"""
    result = subprocess.run(
        [ADB_PATH, "-s", device_id, "exec-out", "screencap", "-p"],
        capture_output=True
    )
    image = Image.open(io.BytesIO(result.stdout))
    rgb = np.array(image)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def main():
    print("=" * 60)
    print("RECALIBRATE: Reward Detection Region")
    print("=" * 60)
    
    # Get devices
    devices = get_devices()
    if not devices:
        print("❌ No devices found!")
        return
    
    print(f"\nFound {len(devices)} device(s):")
    for i, d in enumerate(devices, 1):
        print(f"  {i}. {d}")
    
    # Select device
    if len(devices) == 1:
        device = devices[0]
    else:
        choice = input(f"\nSelect device (1-{len(devices)}): ").strip()
        device = devices[int(choice) - 1]
    
    print(f"\n✓ Using device: {device}")
    
    # Instructions
    print("\n" + "-" * 60)
    print("SETUP:")
    print("  1. Navigate to a battle list with REWARD ICONS visible")
    print("  2. Rewards are the icons on the RIGHT side of battle cards")
    print("-" * 60)
    
    input("\nPress ENTER when rewards are visible on screen...")
    
    # Take screenshot
    print("\nTaking screenshot...")
    img = screenshot(device)
    
    # Scale for display
    h, w = img.shape[:2]
    scale = min(1.0, 900 / h)
    display_w = int(w * scale)
    display_h = int(h * scale)
    display_img = cv2.resize(img, (display_w, display_h))
    
    print(f"  Original: {w}x{h}")
    print(f"  Display:  {display_w}x{display_h} (scale: {scale:.2f})")
    
    # Collect points
    points = []
    display_copy = display_img.copy()
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            # Convert to actual coordinates
            actual_x = int(x / scale)
            actual_y = int(y / scale)
            points.append((actual_x, actual_y))
            
            print(f"  ✓ Point {len(points)}: ({actual_x}, {actual_y})")
            
            cv2.circle(display_copy, (x, y), 5, (0, 0, 255), -1)
            
            if len(points) == 2:
                p1 = (int(points[0][0] * scale), int(points[0][1] * scale))
                p2 = (x, y)
                cv2.rectangle(display_copy, p1, p2, (0, 255, 0), 2)
            
            cv2.imshow("Reward Region", display_copy)
    
    cv2.namedWindow("Reward Region")
    cv2.setMouseCallback("Reward Region", mouse_callback)
    cv2.imshow("Reward Region", display_copy)
    
    print("\n📍 RIGHT CLICK on TOP-LEFT corner of reward area")
    while len(points) < 1:
        cv2.waitKey(1)
    
    print("📍 RIGHT CLICK on BOTTOM-RIGHT corner of reward area")
    while len(points) < 2:
        cv2.waitKey(1)
    
    print("\nPress SPACE to confirm")
    while True:
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    
    cv2.destroyAllWindows()
    
    # Calculate region
    x1, y1 = points[0]
    x2, y2 = points[1]
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    
    print(f"\n✓ New reward region: x={x}, y={y}, w={w}, h={h}")
    
    # Load existing config
    try:
        with open('adb_config.json', 'r') as f:
            config = json.load(f)
    except:
        config = {}
    
    # Update reward region
    config['reward_detection_region'] = [x, y, w, h]
    
    # Save
    with open('adb_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Saved to adb_config.json")
    
    # Test detection
    print("\n" + "-" * 60)
    print("TESTING DETECTION...")
    print("-" * 60)
    
    time.sleep(1)
    test_img = screenshot(device)
    
    # Crop to region
    cropped = test_img[y:y+h, x:x+w]
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    
    # Color detection
    color_ranges = [
        ([80, 100, 150], [130, 255, 255]),   # Cyan/Blue
        ([130, 100, 150], [170, 255, 255]),  # Purple
        ([15, 100, 150], [45, 255, 255]),    # Yellow
        ([0, 120, 180], [180, 255, 255])     # Bright
    ]
    
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in color_ranges:
        m = cv2.inRange(hsv, np.array(lower), np.array(upper))
        mask = cv2.bitwise_or(mask, m)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid = 0
    result = test_img.copy()
    for c in contours:
        area = cv2.contourArea(c)
        if 150 < area < 3000:
            valid += 1
            bx, by, bw, bh = cv2.boundingRect(c)
            cv2.rectangle(result, (x+bx, y+by), (x+bx+bw, y+by+bh), (0, 255, 0), 2)
    
    print(f"  Detected {valid} reward icon(s)")
    
    # Show result scaled
    result_display = cv2.resize(result, (display_w, display_h))
    cv2.imshow("Detection Result", result_display)
    print("\nGreen boxes = detected rewards")
    print("Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()