#!/usr/bin/env python3
"""
Recalibrate Reward Detection Region
Defines the exact area where reward icons appear
"""

import json
import cv2
import numpy as np
from adb_controller import ADBController


def recalibrate_reward_region():
    controller = ADBController()
    
    print("="*60)
    print("RECALIBRATE: Reward Detection Region")
    print("="*60)
    print("\nSetup:")
    print("  1. Navigate to a battle list screen")
    print("  2. Make sure battles with REWARD ICONS are visible")
    print("  3. We'll define the RIGHT SIDE area where rewards appear")
    
    input("\nPress ENTER when on battle list screen...")
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    points = []
    screenshot_display = screenshot.copy()
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            points.append((x, y))
            print(f"  ✓ Point {len(points)}: ({x}, {y})")
            
            # Draw point
            cv2.circle(screenshot_display, (x, y), 5, (0, 0, 255), -1)
            
            # Draw rectangle if we have 2 points
            if len(points) == 2:
                cv2.rectangle(screenshot_display, points[0], points[1], (0, 255, 0), 2)
            
            cv2.imshow("Calibration", screenshot_display)
    
    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_callback)
    cv2.imshow("Calibration", screenshot_display)
    
    print("\nDefine the REWARD DETECTION REGION:")
    print("  1. RIGHT CLICK on TOP-LEFT corner (where rewards start)")
    print("     This should be on the RIGHT SIDE of battle cards")
    
    while len(points) < 1:
        cv2.waitKey(1)
    
    print("  2. RIGHT CLICK on BOTTOM-RIGHT corner (end of reward area)")
    print("     Include the entire right edge of the screen")
    
    while len(points) < 2:
        cv2.waitKey(1)
    
    print("\nPress SPACE to confirm the region")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            break
    
    cv2.destroyAllWindows()
    
    # Calculate region
    x1, y1 = points[0]
    x2, y2 = points[1]
    
    # Ensure top-left to bottom-right
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    
    reward_region = (x, y, w, h)
    
    print(f"\n✓ Reward detection region: x={x}, y={y}, w={w}, h={h}")
    
    # Test detection in this region
    print("\nTesting reward detection in this region...")
    test_detection(controller, reward_region)
    
    response = input("\nDid it detect the rewards correctly? (y/n): ").lower()
    
    if response == 'y':
        # Save to config
        try:
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        config['reward_detection_region'] = list(reward_region)
        
        with open('adb_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✓ Saved reward detection region to adb_config.json")
    else:
        print("\n✗ Try calibrating again with a different region")


def test_detection(controller, region):
    """Test reward detection in the specified region"""
    x, y, w, h = region
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    # Crop to reward region
    cropped = screenshot[y:y+h, x:x+w]
    
    # Convert to HSV
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    
    # Simplified color ranges for reward icons
    # Looking for ANY bright, saturated colors
    color_ranges = [
        # Cyan/Blue (magnifying glass, hourglass rim)
        ([80, 100, 150], [130, 255, 255]),
        
        # Purple/Magenta (hourglass)
        ([130, 100, 150], [170, 255, 255]),
        
        # Yellow/Gold
        ([15, 100, 150], [45, 255, 255]),
        
        # Any bright color (catch-all)
        ([0, 120, 180], [180, 255, 255])
    ]
    
    # Combine masks
    combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    
    for lower, upper in color_ranges:
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    
    # Find contours
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"  Found {len(contours)} potential reward icon(s)")
    
    # Draw on original screenshot for visualization
    result = screenshot.copy()
    
    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by size
        if 150 < area < 3000:
            bx, by, bw, bh = cv2.boundingRect(contour)
            
            # Convert back to full screen coordinates
            full_x = x + bx + bw // 2
            full_y = y + by + bh // 2
            
            detections.append((full_x, full_y, area))
            
            # Draw on result
            cv2.rectangle(result, (x + bx, y + by), (x + bx + bw, y + by + bh), (0, 255, 0), 2)
            cv2.circle(result, (full_x, full_y), 5, (0, 0, 255), -1)
    
    print(f"  Detected {len(detections)} reward icon(s) after filtering")
    
    # Show result
    cv2.imshow("Detection Test", result)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    
    return detections


if __name__ == "__main__":
    recalibrate_reward_region()