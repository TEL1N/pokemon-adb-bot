#!/usr/bin/env python3
"""
TEST 02: ADB Calibration (VISUAL METHOD - RIGHT CLICK)
Complete workflow with clear navigation steps
"""

import json
import cv2
import numpy as np
from adb_controller import ADBController


class VisualCalibrator:
    def __init__(self, device_id="emulator-5556"):
        self.controller = ADBController(device_id)
        self.config = {}
        self.current_screenshot = None
        self.clicked_point = None
        
        # Get screen dimensions
        self.width, self.height = self.controller.get_screen_size()
        print(f"✓ Emulator screen: {self.width}x{self.height}")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks on the screenshot window - RIGHT CLICK to capture"""
        if event == cv2.EVENT_RBUTTONDOWN:  # RIGHT CLICK
            self.clicked_point = (x, y)
            
            # Draw a marker on the screenshot
            display_img = self.current_screenshot.copy()
            cv2.circle(display_img, (x, y), 10, (0, 0, 255), 2)
            cv2.circle(display_img, (x, y), 3, (0, 0, 255), -1)
            cv2.putText(display_img, f"({x}, {y})", (x+15, y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("Calibration", display_img)
            print(f"  ✓ Captured: ({x}, {y}) - Press SPACE to confirm")
    
    def get_point_from_click(self, window_name, prompt):
        """
        Show screenshot, let user RIGHT CLICK, return coordinates
        """
        print(f"\n{prompt}")
        print("  → RIGHT CLICK on the screenshot at the desired position")
        print("  → Press SPACE to confirm")
        print("  → Press 'r' to retake screenshot")
        print("  → Press 'q' to skip")
        
        self.clicked_point = None
        
        # Take screenshot
        self.current_screenshot = self.controller.screenshot_cv()
        
        display_img = self.current_screenshot.copy()
        
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        cv2.imshow(window_name, display_img)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and self.clicked_point:
                # Confirm selection
                print(f"  ✓ Confirmed: {self.clicked_point}")
                return self.clicked_point
            
            elif key == ord('r'):
                # Retake screenshot
                print("  Retaking screenshot...")
                self.current_screenshot = self.controller.screenshot_cv()
                display_img = self.current_screenshot.copy()
                cv2.imshow(window_name, display_img)
                self.clicked_point = None
            
            elif key == ord('q'):
                # Skip
                print("  Skipped")
                return None
    
    def test_coordinate(self, x, y):
        """Test a coordinate by tapping it in the emulator"""
        print(f"\n  Testing coordinate ({x}, {y}) in emulator...")
        print("  Watch your emulator!")
        import time
        time.sleep(1)
        self.controller.tap(x, y)
        
        response = input("  Was that the correct position? (y/n): ").lower()
        return response == 'y'
    
    def calibrate_with_test(self, window_name, prompt):
        """Get point and verify by testing"""
        while True:
            point = self.get_point_from_click(window_name, prompt)
            
            if point is None:
                return None
            
            x, y = point
            
            # Test the coordinate
            if self.test_coordinate(x, y):
                return point
            else:
                print("  Let's try again...")
                continue
    
    # ===== STEP 1: BATTLE UI =====
    def calibrate_battle_ui(self):
        """Calibrate AUTO and BATTLE buttons"""
        print("\n" + "="*60)
        print("STEP 1: Battle UI (AUTO + BATTLE buttons)")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. Start any battle in the emulator")
        print("  2. Make sure AUTO and BATTLE buttons are visible")
        
        input("\n✓ Press ENTER when you're on a battle screen...")
        
        # AUTO button
        auto_pos = self.calibrate_with_test(
            "Calibration - AUTO button",
            "📍 RIGHT CLICK on the AUTO button"
        )
        if auto_pos:
            self.config["auto_button"] = list(auto_pos)
        
        # BATTLE button
        battle_pos = self.calibrate_with_test(
            "Calibration - BATTLE button",
            "📍 RIGHT CLICK on the BATTLE button"
        )
        if battle_pos:
            self.config["battle_button"] = list(battle_pos)
        
        cv2.destroyAllWindows()
        print("✓ Battle UI calibrated")
    
    # ===== STEP 2: MAIN MENU NAVIGATION =====
    def calibrate_main_menu(self):
        """Calibrate main menu navigation"""
        print("\n" + "="*60)
        print("STEP 2: Main Menu Navigation")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. Press BACK button to return to main menu")
        print("  2. You should see the main tabs at the bottom")
        
        input("\n✓ Press ENTER when you're at the main menu...")
        
        # BATTLES tab
        battles_tab = self.calibrate_with_test(
            "Calibration - BATTLES Tab",
            "📍 RIGHT CLICK on the BATTLES tab (bottom navigation)"
        )
        if battles_tab:
            self.config["battles_tab"] = list(battles_tab)
        
        cv2.destroyAllWindows()
        print("✓ Battles tab calibrated")
    
    # ===== STEP 3: SOLO BATTLES =====
    def calibrate_solo_battles(self):
        """Calibrate Solo Battles button"""
        print("\n" + "="*60)
        print("STEP 3: Solo Battles Screen")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. Click the BATTLES tab if you haven't already")
        print("  2. You should see SOLO BATTLE button")
        
        input("\n✓ Press ENTER when ready...")
        
        # SOLO BATTLE button
        solo_battle = self.calibrate_with_test(
            "Calibration - SOLO BATTLE",
            "📍 RIGHT CLICK on the SOLO BATTLE button"
        )
        if solo_battle:
            self.config["solo_battle_button"] = list(solo_battle)
            
            # Click it to navigate
            print("\n  Clicking SOLO BATTLE...")
            self.controller.tap(*solo_battle)
            import time
            time.sleep(2)
        
        cv2.destroyAllWindows()
        print("✓ Solo Battle calibrated")
    
    # ===== STEP 4: DIFFICULTY BUTTONS =====
    def calibrate_difficulty_buttons(self):
        """Calibrate difficulty buttons with scroll"""
        print("\n" + "="*60)
        print("STEP 4: Difficulty Buttons")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. You should be on the Solo Battle screen")
        print("  2. We need to scroll down to reveal difficulty options")
        print("  3. We'll perform 2 swipe gestures to scroll down")
        
        input("\n✓ Press ENTER to calibrate scroll gesture...")
        
        # Calibrate scroll gesture for difficulty reveal
        print("\n📍 Scroll gesture to reveal difficulties")
        
        scroll_start = self.get_point_from_click(
            "Calibration - Scroll START",
            "📍 RIGHT CLICK where the swipe should START (bottom-middle of screen)"
        )
        
        scroll_end = self.get_point_from_click(
            "Calibration - Scroll END",
            "📍 RIGHT CLICK where the swipe should END (top-middle of screen)"
        )
        
        if scroll_start and scroll_end:
            self.config["difficulty_scroll"] = {
                "start": list(scroll_start),
                "end": list(scroll_end)
            }
            
            # Test scroll twice
            print("\n  Testing scroll gesture (2 times)...")
            self.controller.swipe(*scroll_start, *scroll_end)
            import time
            time.sleep(1)
            self.controller.swipe(*scroll_start, *scroll_end)
            time.sleep(1)
            
            input("  Did the screen scroll to reveal difficulties? Press ENTER...")
        
        # Now calibrate difficulty buttons
        print("\n📍 Difficulty buttons should now be visible")
        
        difficulties = {}
        for diff_name in ["beginner","intermediate", "advanced", "expert"]:
            pos = self.calibrate_with_test(
                f"Calibration - {diff_name.upper()}",
                f"📍 RIGHT CLICK on the {diff_name.upper()} difficulty button"
            )
            if pos:
                difficulties[diff_name] = list(pos)
        
        if difficulties:
            self.config["difficulty_buttons"] = difficulties
        
        cv2.destroyAllWindows()
        print("✓ Difficulties calibrated")
    
    # ===== STEP 5: EXPANSIONS MENU =====
    def calibrate_expansions_menu(self):
        """Calibrate expansions menu"""
        print("\n" + "="*60)
        print("STEP 5: Expansions Menu")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. Press BACK to return to main menu")
        print("  2. Find the EXPANSIONS tab/button")
        
        input("\n✓ Press ENTER when ready...")
        
        # EXPANSIONS button/tab
        exp_button = self.calibrate_with_test(
            "Calibration - EXPANSIONS Tab",
            "📍 RIGHT CLICK on the EXPANSIONS tab/button"
        )
        if exp_button:
            self.config["expansions_button"] = list(exp_button)
            
            # Click it to open
            print("\n  Opening expansions menu...")
            self.controller.tap(*exp_button)
            import time
            time.sleep(2)
        
        cv2.destroyAllWindows()
        print("✓ Expansions button calibrated")
    
    # ===== STEP 6: SERIES BUTTONS =====
    def calibrate_series_buttons(self):
        """Calibrate A/B series buttons"""
        print("\n" + "="*60)
        print("STEP 6: Series Buttons (A/B)")
        print("="*60)
        print("\n⚠️  You should see the expansions menu with A and B series buttons")
        
        input("\n✓ Press ENTER when ready...")
        
        series = {}
        
        # B series first (as you requested)
        b_pos = self.calibrate_with_test(
            "Calibration - B SERIES",
            "📍 RIGHT CLICK on the B-SERIES button"
        )
        if b_pos:
            series["B"] = list(b_pos)
        
        # A series
        a_pos = self.calibrate_with_test(
            "Calibration - A SERIES",
            "📍 RIGHT CLICK on the A-SERIES button"
        )
        if a_pos:
            series["A"] = list(a_pos)
        
        if series:
            self.config["series_buttons"] = series
        
        cv2.destroyAllWindows()
        print("✓ Series buttons calibrated")
    
    # ===== STEP 7: EXPANSION SCROLL =====
    def calibrate_expansion_scroll(self):
        """Calibrate expansion list scroll gesture"""
        print("\n" + "="*60)
        print("STEP 7: Expansion List Scroll Gesture")
        print("="*60)
        print("\n⚠️  SETUP:")
        print("  1. You should see a list of expansions")
        print("  2. We need to calibrate the EXACT swipe gesture")
        print("  3. This gesture reveals ONE expansion at a time")
        
        input("\n✓ Press ENTER when ready...")
        
        # Scroll gesture
        scroll_start = self.get_point_from_click(
            "Calibration - Expansion Scroll START",
            "📍 RIGHT CLICK where swipe should BEGIN (bottom of expansion list)"
        )
        
        scroll_end = self.get_point_from_click(
            "Calibration - Expansion Scroll END",
            "📍 RIGHT CLICK where swipe should END/LIFT (top of expansion list)"
        )
        
        if scroll_start and scroll_end:
            self.config["expansion_scroll"] = {
                "start": list(scroll_start),
                "end": list(scroll_end)
            }
            
            # Test the scroll
            print("\n  Testing expansion scroll gesture...")
            print("  Watch if ONE expansion scrolls into view...")
            self.controller.swipe(*scroll_start, *scroll_end, duration=400)
            import time
            time.sleep(1)
            
            response = input("  Did it scroll correctly (one expansion revealed)? (y/n): ").lower()
            if response == 'y':
                print("  ✓ Scroll gesture looks good!")
            else:
                print("  ⚠️  You may need to adjust this later")
        
        cv2.destroyAllWindows()
        print("✓ Expansion scroll calibrated")
    
    # ===== STEP 8: EXPANSION SLOTS =====
    def calibrate_expansion_slots(self):
        """Calibrate expansion card positions"""
        print("\n" + "="*60)
        print("STEP 8: Expansion Card Positions")
        print("="*60)
        print("\n⚠️  We need to calibrate 3 expansion card positions:")
        print("  1. TOP visible expansion")
        print("  2. MIDDLE visible expansion")
        print("  3. BOTTOM visible expansion")
        
        input("\n✓ Press ENTER when ready...")
        
        slots = []
        for i, position in enumerate(["TOP", "MIDDLE", "BOTTOM"], 1):
            pos = self.calibrate_with_test(
                f"Calibration - Expansion Slot {i}",
                f"📍 RIGHT CLICK on the {position} expansion card"
            )
            if pos:
                slots.append(list(pos))
        
        if slots:
            self.config["expansion_slots"] = slots
        
        cv2.destroyAllWindows()
        print("✓ Expansion slots calibrated")
    
    def save_config(self, filename="adb_config.json"):
        """Save configuration"""
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"\n✓ Configuration saved: {filename}")
    
    def run_full_calibration(self):
        """Run complete calibration workflow"""
        print("\n" + "="*60)
        print("VISUAL CALIBRATION WIZARD - COMPLETE WORKFLOW")
        print("="*60)
        print("\nHow it works:")
        print("  1. Screenshot of emulator appears")
        print("  2. RIGHT CLICK on the element you want to calibrate")
        print("  3. Press SPACE to confirm")
        print("  4. Bot will test the coordinate in emulator")
        print("  5. Confirm if correct")
        print("\nCalibration Order:")
        print("  Step 1: Battle UI (AUTO + BATTLE)")
        print("  Step 2: Main Menu (BATTLES tab)")
        print("  Step 3: Solo Battles button")
        print("  Step 4: Difficulty buttons (with scroll)")
        print("  Step 5: Expansions menu")
        print("  Step 6: Series buttons (B + A)")
        print("  Step 7: Expansion scroll gesture")
        print("  Step 8: Expansion card positions")
        
        input("\nPress ENTER to begin...")
        
        # Run calibration steps IN ORDER
        self.calibrate_battle_ui()
        self.calibrate_main_menu()
        self.calibrate_solo_battles()
        self.calibrate_difficulty_buttons()
        self.calibrate_expansions_menu()
        self.calibrate_series_buttons()
        self.calibrate_expansion_scroll()
        self.calibrate_expansion_slots()
        
        # Save
        self.save_config()
        
        # Summary
        print("\n" + "="*60)
        print("CALIBRATION COMPLETE!")
        print("="*60)
        print("\nCalibrated coordinates:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
        
        print("\n✓✓✓ Ready for Test 03 (Battle Detection) ✓✓✓")


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 02: VISUAL CALIBRATION")
    print("="*60)
    
    calibrator = VisualCalibrator(None)
    calibrator.run_full_calibration()


if __name__ == "__main__":
    main()