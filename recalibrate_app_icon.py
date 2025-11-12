#!/usr/bin/env python3
"""
Quick recalibration for app icon only
"""

import json
import cv2
from adb_controller import ADBController


def recalibrate_app_icon():
    controller = ADBController()
    
    print("="*60)
    print("RECALIBRATE: Pokemon TCG App Icon")
    print("="*60)
    print("\nSetup:")
    print("  1. Press HOME button on your emulator")
    print("  2. You should see the Pokemon TCG Pocket app icon")
    
    input("\nPress ENTER when on home screen...")
    
    # Go to home screen
    print("Pressing HOME button...")
    controller.press_home(delay=2)
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    clicked_point = None
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal clicked_point
        if event == cv2.EVENT_RBUTTONDOWN:
            clicked_point = (x, y)
            print(f"  ✓ Captured: ({x}, {y})")
            cv2.circle(screenshot, (x, y), 10, (0, 0, 255), 2)
            cv2.imshow("Calibration", screenshot)
    
    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_callback)
    cv2.imshow("Calibration", screenshot)
    
    print("\nRIGHT CLICK on the Pokemon TCG Pocket app icon")
    print("Then press SPACE to confirm")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and clicked_point:
            break
    
    cv2.destroyAllWindows()
    
    print(f"\n✓ App icon position: {clicked_point}")
    
    # Test it
    print("\nTesting app icon tap...")
    controller.tap(*clicked_point)
    time.sleep(3)
    
    response = input("\nDid it open Pokemon TCG? (y/n): ").lower()
    
    if response == 'y':
        # Load existing config
        try:
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        # Update app icon
        config['pokemon_app_icon'] = list(clicked_point)
        
        # Save
        with open('adb_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✓ Saved app icon to adb_config.json")
    else:
        print("\n✗ Try recalibrating again")


if __name__ == "__main__":
    import time
    recalibrate_app_icon()