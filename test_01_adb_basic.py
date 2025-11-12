#!/usr/bin/env python3
"""
TEST 01: Basic ADB Functions
Tests that ADB controller can:
1. Connect to device
2. Take screenshots
3. Perform taps
4. Perform swipes
5. Press keys
"""

import time
from adb_controller import ADBController


def test_connection():
    """Test 1: Device Connection"""
    print("\n" + "="*60)
    print("TEST 1: Device Connection")
    print("="*60)
    
    try:
        controller = ADBController("emulator-5556")
        print("✓ Successfully connected to emulator-5556")
        return controller
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None


def test_screen_info(controller):
    """Test 2: Screen Information"""
    print("\n" + "="*60)
    print("TEST 2: Screen Information")
    print("="*60)
    
    width, height = controller.get_screen_size()
    print(f"✓ Screen size: {width}x{height}")
    
    return width, height


def test_screenshot(controller):
    """Test 3: Screenshot Capture"""
    print("\n" + "="*60)
    print("TEST 3: Screenshot Capture")
    print("="*60)
    
    print("Taking screenshot...")
    controller.save_screenshot("test_01_screenshot.png")
    
    print("✓ Check your project folder for 'test_01_screenshot.png'")
    input("Press ENTER after you verify the screenshot looks correct...")


def test_tap(controller, width, height):
    """Test 4: Tap Input"""
    print("\n" + "="*60)
    print("TEST 4: Tap Input")
    print("="*60)
    
    print("We will tap the CENTER of the screen in 3 seconds...")
    print("Watch your emulator!")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    center_x = width // 2
    center_y = height // 2
    
    controller.tap(center_x, center_y)
    
    print(f"✓ Tapped at ({center_x}, {center_y})")
    response = input("Did you see the tap register in the emulator? (y/n): ")
    
    if response.lower() == 'y':
        print("✓ Tap test PASSED")
        return True
    else:
        print("✗ Tap test FAILED")
        return False


def test_swipe(controller, width, height):
    """Test 5: Swipe Input"""
    print("\n" + "="*60)
    print("TEST 5: Swipe Input")
    print("="*60)
    
    print("We will swipe DOWN (top to bottom) in 3 seconds...")
    print("Watch your emulator!")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # Swipe from middle-top to middle-bottom
    start_x = width // 2
    start_y = int(height * 0.3)
    end_x = width // 2
    end_y = int(height * 0.7)
    
    controller.swipe(start_x, start_y, end_x, end_y, duration=400)
    
    print(f"✓ Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    response = input("Did you see the swipe/scroll happen in the emulator? (y/n): ")
    
    if response.lower() == 'y':
        print("✓ Swipe test PASSED")
        return True
    else:
        print("✗ Swipe test FAILED")
        return False


def test_back_button(controller):
    """Test 6: Back Button"""
    print("\n" + "="*60)
    print("TEST 6: Back Button")
    print("="*60)
    
    print("We will press the BACK button in 3 seconds...")
    print("Watch your emulator!")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    controller.press_back()
    
    print("✓ Pressed BACK button")
    response = input("Did the back button action happen? (y/n): ")
    
    if response.lower() == 'y':
        print("✓ Back button test PASSED")
        return True
    else:
        print("✗ Back button test FAILED")
        return False


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 01: BASIC FUNCTIONS")
    print("="*60)
    print("\nThis test verifies ADB can control your emulator.")
    print("Make sure Pokemon TCG Pocket is open in Mumuplayer!")
    
    input("\nPress ENTER to start tests...")
    
    # Test 1: Connection
    controller = test_connection()
    if not controller:
        print("\n✗ Cannot proceed without connection")
        return
    
    # Test 2: Screen Info
    width, height = test_screen_info(controller)
    
    # Test 3: Screenshot
    test_screenshot(controller)
    
    # Test 4: Tap
    tap_result = test_tap(controller, width, height)
    
    # Test 5: Swipe
    swipe_result = test_swipe(controller, width, height)
    
    # Test 6: Back Button
    back_result = test_back_button(controller)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Connection:  ✓ PASSED")
    print(f"Screen Info: ✓ PASSED")
    print(f"Screenshot:  ✓ PASSED")
    print(f"Tap:         {'✓ PASSED' if tap_result else '✗ FAILED'}")
    print(f"Swipe:       {'✓ PASSED' if swipe_result else '✗ FAILED'}")
    print(f"Back Button: {'✓ PASSED' if back_result else '✗ FAILED'}")
    
    all_passed = tap_result and swipe_result and back_result
    
    if all_passed:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("Ready to proceed to Test 02 (Calibration)")
    else:
        print("\n✗ Some tests failed. Check your ADB connection.")


if __name__ == "__main__":
    main()