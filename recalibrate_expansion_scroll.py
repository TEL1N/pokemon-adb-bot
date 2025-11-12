#!/usr/bin/env python3
"""
Quick recalibration for expansion scroll gesture only
"""

import json
import cv2
from adb_controller import ADBController


def recalibrate_scroll():
    controller = ADBController("emulator-5556")
    
    print("="*60)
    print("RECALIBRATE: Expansion Scroll Gesture")
    print("="*60)
    print("\nThe scroll is overshooting. We need shorter distance.")
    print("\nSetup:")
    print("  1. Open the Expansions menu in your emulator")
    print("  2. You should see a list of expansions")
    
    input("\nPress ENTER when ready...")
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    clicked_points = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            clicked_points.append((x, y))
            print(f"  ✓ Point {len(clicked_points)}: ({x}, {y})")
            cv2.circle(screenshot, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Calibration", screenshot)
    
    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_callback)
    cv2.imshow("Calibration", screenshot)
    
    print("\nRIGHT CLICK on the START point (where scroll begins)")
    print("Make this HIGHER UP than before to reduce scroll distance")
    
    while len(clicked_points) < 1:
        cv2.waitKey(1)
    
    print("\nRIGHT CLICK on the END point (where scroll ends)")
    print("Make this LOWER DOWN than before to reduce scroll distance")
    
    while len(clicked_points) < 2:
        cv2.waitKey(1)
    
    cv2.destroyAllWindows()
    
    start_point = clicked_points[0]
    end_point = clicked_points[1]
    
    print(f"\n✓ New scroll gesture:")
    print(f"  Start: {start_point}")
    print(f"  End: {end_point}")
    
    # Test it
    print("\nTesting new scroll gesture...")
    controller.swipe(*start_point, *end_point, duration=400, delay=1.2)
    
    response = input("\nDid it scroll correctly (ONE expansion revealed)? (y/n): ").lower()
    
    if response == 'y':
        # Load existing config
        try:
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        # Update scroll gesture
        config['expansion_scroll'] = {
            'start': list(start_point),
            'end': list(end_point)
        }
        
        # Save
        with open('adb_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✓ Saved new scroll gesture to adb_config.json")
        print("You can now run test_04 again!")
    else:
        print("\n✗ Try recalibrating again with different points")


if __name__ == "__main__":
    recalibrate_scroll()