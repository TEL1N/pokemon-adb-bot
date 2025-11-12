#!/usr/bin/env python3
"""
Quick recalibration for A/B series buttons only
"""

import json
import cv2
import time
from adb_controller import ADBController


def recalibrate_series_buttons():
    controller = ADBController()
    
    print("="*60)
    print("RECALIBRATE: A/B Series Buttons")
    print("="*60)
    print("\nSetup:")
    print("  1. Navigate to the Expansions menu")
    print("  2. Make sure A and B series buttons are visible")
    
    input("\nPress ENTER when on Expansions screen...")
    
    # Navigate to expansions
    try:
        with open('adb_config.json', 'r') as f:
            config = json.load(f)
        
        expansions_button = tuple(config.get("expansions_button", (0, 0)))
        if expansions_button != (0, 0):
            print("\nOpening Expansions menu...")
            controller.tap(*expansions_button)
            time.sleep(2)
    except:
        print("\n⚠️ No config found, make sure you're on Expansions screen")
    
    # Take screenshot
    screenshot = controller.screenshot_cv()
    
    series_buttons = {}
    
    # Calibrate B-series first
    print("\n" + "="*60)
    print("CALIBRATE: B-SERIES BUTTON")
    print("="*60)
    
    clicked_point = None
    screenshot_copy = screenshot.copy()
    
    def mouse_callback_b(event, x, y, flags, param):
        nonlocal clicked_point
        if event == cv2.EVENT_RBUTTONDOWN:
            clicked_point = (x, y)
            print(f"  ✓ Captured B-series: ({x}, {y})")
            cv2.circle(screenshot_copy, (x, y), 10, (0, 0, 255), 2)
            cv2.imshow("Calibration - B Series", screenshot_copy)
    
    cv2.namedWindow("Calibration - B Series")
    cv2.setMouseCallback("Calibration - B Series", mouse_callback_b)
    cv2.imshow("Calibration - B Series", screenshot_copy)
    
    print("\nRIGHT CLICK on the B-SERIES button")
    print("(Look for the 'B' tab/button)")
    print("Then press SPACE to confirm")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and clicked_point:
            break
    
    cv2.destroyAllWindows()
    
    b_pos = clicked_point
    print(f"\n✓ B-series position: {b_pos}")
    
    # Test B button
    print("\nTesting B-series button...")
    controller.tap(*b_pos)
    time.sleep(2)
    
    response = input("Did it switch to B-series? (y/n): ").lower()
    if response == 'y':
        series_buttons["B"] = list(b_pos)
    else:
        print("✗ B-series button failed, skipping...")
        return
    
    # Calibrate A-series
    print("\n" + "="*60)
    print("CALIBRATE: A-SERIES BUTTON")
    print("="*60)
    
    # Take fresh screenshot (after B click)
    time.sleep(1)
    screenshot = controller.screenshot_cv()
    clicked_point = None
    screenshot_copy = screenshot.copy()
    
    def mouse_callback_a(event, x, y, flags, param):
        nonlocal clicked_point
        if event == cv2.EVENT_RBUTTONDOWN:
            clicked_point = (x, y)
            print(f"  ✓ Captured A-series: ({x}, {y})")
            cv2.circle(screenshot_copy, (x, y), 10, (0, 255, 0), 2)
            cv2.imshow("Calibration - A Series", screenshot_copy)
    
    cv2.namedWindow("Calibration - A Series")
    cv2.setMouseCallback("Calibration - A Series", mouse_callback_a)
    cv2.imshow("Calibration - A Series", screenshot_copy)
    
    print("\nRIGHT CLICK on the A-SERIES button")
    print("(Look for the 'A' tab/button)")
    print("Then press SPACE to confirm")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and clicked_point:
            break
    
    cv2.destroyAllWindows()
    
    a_pos = clicked_point
    print(f"\n✓ A-series position: {a_pos}")
    
    # Test A button
    print("\nTesting A-series button...")
    controller.tap(*a_pos)
    time.sleep(2)
    
    response = input("Did it switch to A-series? (y/n): ").lower()
    if response == 'y':
        series_buttons["A"] = list(a_pos)
    else:
        print("✗ A-series button failed, skipping...")
        return
    
    # Save to config
    try:
        with open('adb_config.json', 'r') as f:
            config = json.load(f)
    except:
        config = {}
    
    config['series_buttons'] = series_buttons
    
    with open('adb_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "="*60)
    print("✓ SERIES BUTTONS RECALIBRATED")
    print("="*60)
    print(f"A-series: {series_buttons.get('A')}")
    print(f"B-series: {series_buttons.get('B')}")
    print("\n✓ Saved to adb_config.json")


if __name__ == "__main__":
    recalibrate_series_buttons()