#!/usr/bin/env python3
"""
IMPROVED CALIBRATION SCRIPT
- Supports device-specific configs for multi-instance
- Better validation and testing
- Clearer instructions
"""

import json
import cv2
import time
import sys
import os

# Add parent directory to path if running from different location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# We'll inline the ADBController to avoid import issues
import subprocess
import numpy as np
from PIL import Image
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
        print(f"✓ ADB Controller initialized for: {self.device}")
    
    def _run_adb_command(self, command):
        full_command = [self.ADB_PATH, "-s", self.device] + command
        return subprocess.run(full_command, capture_output=True, text=True)
    
    def tap(self, x, y, delay=0.3):
        print(f"  [ADB] Tap at ({x}, {y})")
        self._run_adb_command(["shell", "input", "tap", str(x), str(y)])
        time.sleep(delay)
    
    def swipe(self, x1, y1, x2, y2, duration=400, delay=0.5):
        print(f"  [ADB] Swipe from ({x1}, {y1}) to ({x2}, {y2})")
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
        if result.returncode != 0:
            raise Exception(f"Screenshot failed")
        image = Image.open(io.BytesIO(result.stdout))
        rgb_array = np.array(image)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return bgr_array
    
    def get_screen_size(self):
        result = self._run_adb_command(["shell", "wm", "size"])
        if "Physical size:" in result.stdout:
            dimensions = result.stdout.strip().split(": ")[1]
            width, height = map(int, dimensions.split("x"))
            return (width, height)
        img = self.screenshot_cv()
        height, width = img.shape[:2]
        return (width, height)


class ImprovedCalibrator:
    def __init__(self, device_id=None, use_device_specific_config=False):
        """
        Initialize calibrator
        
        Args:
            device_id: Specific device to calibrate, or None for auto-detect
            use_device_specific_config: If True, saves to adb_config_<device>.json
        """
        self.controller = ADBController(device_id)
        self.device_id = self.controller.device
        self.use_device_specific = use_device_specific_config
        
        self.config = {}
        self.current_screenshot = None
        self.current_screenshot_display = None  # Scaled version for display
        self.clicked_point = None
        
        self.width, self.height = self.controller.get_screen_size()
        print(f"✓ Emulator screen size: {self.width}x{self.height}")
        
        # Calculate display scale to fit on monitor
        # Target max height of 900 pixels for comfortable viewing
        self.max_display_height = 900
        self.display_scale = min(1.0, self.max_display_height / self.height)
        self.display_width = int(self.width * self.display_scale)
        self.display_height = int(self.height * self.display_scale)
        
        print(f"✓ Display scale: {self.display_scale:.2f} ({self.display_width}x{self.display_height})")
        
        # Determine config filename
        if use_device_specific_config:
            sanitized = self.device_id.replace(":", "_").replace(".", "_")
            self.config_file = f"adb_config_{sanitized}.json"
        else:
            self.config_file = "adb_config.json"
        
        print(f"✓ Will save to: {self.config_file}")
    
    def get_config_filename(self):
        return self.config_file
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            # Convert display coordinates back to actual emulator coordinates
            actual_x = int(x / self.display_scale)
            actual_y = int(y / self.display_scale)
            self.clicked_point = (actual_x, actual_y)
            
            # Draw on display image
            display_img = self.current_screenshot_display.copy()
            cv2.circle(display_img, (x, y), 8, (0, 0, 255), 2)
            cv2.circle(display_img, (x, y), 3, (0, 0, 255), -1)
            cv2.putText(display_img, f"({actual_x}, {actual_y})", (x+10, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow("Calibration", display_img)
            print(f"  ✓ Captured: ({actual_x}, {actual_y}) - Press SPACE to confirm, R to retry")
    
    def get_point_from_click(self, window_name, prompt):
        """Get point via RIGHT CLICK (with scaled display)"""
        print(f"\n{prompt}")
        print("  → RIGHT CLICK on the screenshot")
        print("  → Press SPACE to confirm")
        print("  → Press R to retake screenshot")
        print("  → Press Q to skip")
        
        self.clicked_point = None
        self.current_screenshot = self.controller.screenshot_cv()
        
        # Create scaled display version
        self.current_screenshot_display = cv2.resize(
            self.current_screenshot, 
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_AREA
        )
        
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        cv2.imshow(window_name, self.current_screenshot_display)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and self.clicked_point:
                print(f"  ✓ Confirmed: {self.clicked_point}")
                cv2.destroyWindow(window_name)
                return self.clicked_point
            elif key == ord('r'):
                print("  Retaking screenshot...")
                self.current_screenshot = self.controller.screenshot_cv()
                self.current_screenshot_display = cv2.resize(
                    self.current_screenshot, 
                    (self.display_width, self.display_height),
                    interpolation=cv2.INTER_AREA
                )
                cv2.imshow(window_name, self.current_screenshot_display)
                self.clicked_point = None
            elif key == ord('q'):
                print("  Skipped")
                cv2.destroyWindow(window_name)
                return None
    
    def test_and_confirm(self, x, y, description):
        """Test a coordinate and ask for confirmation"""
        print(f"\n  Testing {description} at ({x}, {y})...")
        print("  Watch your emulator!")
        time.sleep(0.5)
        self.controller.tap(x, y)
        time.sleep(1)
        
        response = input(f"  Was that the correct {description}? (y/n): ").lower()
        return response == 'y'
    
    def calibrate_with_verification(self, window_name, prompt, description):
        """Calibrate with tap verification"""
        while True:
            point = self.get_point_from_click(window_name, prompt)
            if point is None:
                return None
            
            x, y = point
            if self.test_and_confirm(x, y, description):
                return point
            else:
                print("  Let's try again...")
    
    # ==================== CALIBRATION STEPS ====================
    
    def step_app_icon(self):
        """Step 0: App icon on home screen"""
        print("\n" + "=" * 60)
        print("STEP 0: Pokemon TCG App Icon")
        print("=" * 60)
        print("\nSetup:")
        print("  1. Press HOME on your emulator")
        print("  2. Make sure Pokemon TCG Pocket icon is visible")
        
        input("\nPress ENTER when on home screen...")
        
        self.controller.press_home(delay=2)
        
        app_icon = self.calibrate_with_verification(
            "Calibration - App Icon",
            "📍 RIGHT CLICK on the Pokemon TCG Pocket app icon",
            "app icon"
        )
        
        if app_icon:
            self.config["pokemon_app_icon"] = list(app_icon)
            print("✓ App icon calibrated")
            
            # Open the app
            print("\nOpening Pokemon TCG Pocket...")
            self.controller.tap(*app_icon)
            time.sleep(5)
    
    def step_battles_tab(self):
        """Step 1: Battles tab"""
        print("\n" + "=" * 60)
        print("STEP 1: Battles Tab")
        print("=" * 60)
        print("\nYou should see the main menu with bottom navigation")
        
        input("\nPress ENTER when ready...")
        
        battles_tab = self.calibrate_with_verification(
            "Calibration - Battles Tab",
            "📍 RIGHT CLICK on the BATTLES tab (bottom navigation)",
            "Battles tab"
        )
        
        if battles_tab:
            self.config["battles_tab"] = list(battles_tab)
            print("✓ Battles tab calibrated")
            
            # Click it
            print("\nNavigating to Battles...")
            self.controller.tap(*battles_tab)
            time.sleep(3)
    
    def step_solo_battle(self):
        """Step 2: Solo Battle button"""
        print("\n" + "=" * 60)
        print("STEP 2: Solo Battle Button")
        print("=" * 60)
        
        input("\nPress ENTER when on Battles screen...")
        
        solo_battle = self.calibrate_with_verification(
            "Calibration - Solo Battle",
            "📍 RIGHT CLICK on SOLO BATTLE button",
            "Solo Battle button"
        )
        
        if solo_battle:
            self.config["solo_battle_button"] = list(solo_battle)
            print("✓ Solo Battle calibrated")
            
            # Click it
            print("\nOpening Solo Battle...")
            self.controller.tap(*solo_battle)
            time.sleep(3)
    
    def step_difficulty_buttons(self):
        """Step 3: Difficulty buttons"""
        print("\n" + "=" * 60)
        print("STEP 3: Difficulty Buttons")
        print("=" * 60)
        print("\nWe need to calibrate:")
        print("  - Scroll gesture to reveal difficulties")
        print("  - Beginner, Intermediate, Advanced, Expert buttons")
        
        input("\nPress ENTER when on Solo Battle screen...")
        
        # First calibrate scroll
        print("\n--- Scroll Gesture ---")
        print("We need a swipe to reveal difficulty options")
        
        scroll_start = self.get_point_from_click(
            "Scroll START",
            "📍 RIGHT CLICK where swipe should START (bottom area)"
        )
        
        scroll_end = self.get_point_from_click(
            "Scroll END",
            "📍 RIGHT CLICK where swipe should END (top area)"
        )
        
        if scroll_start and scroll_end:
            self.config["difficulty_scroll"] = {
                "start": list(scroll_start),
                "end": list(scroll_end)
            }
            
            print("\nTesting scroll (2 times)...")
            self.controller.swipe_with_hold(*scroll_start, *scroll_end, duration=400, hold_time=1000, delay=1)
            time.sleep(0.5)
            self.controller.swipe_with_hold(*scroll_start, *scroll_end, duration=400, hold_time=1000, delay=1)
            
            input("Did difficulties become visible? Press ENTER...")
        
        # Now calibrate difficulty buttons
        print("\n--- Difficulty Buttons ---")
        difficulties = {}
        
        for diff in ["beginner", "intermediate", "advanced", "expert"]:
            pos = self.calibrate_with_verification(
                f"Calibration - {diff.upper()}",
                f"📍 RIGHT CLICK on {diff.upper()} difficulty",
                f"{diff} button"
            )
            if pos:
                difficulties[diff] = list(pos)
        
        if difficulties:
            self.config["difficulty_buttons"] = difficulties
            print("✓ Difficulty buttons calibrated")
    
    def step_expansions_menu(self):
        """Step 4: Expansions menu"""
        print("\n" + "=" * 60)
        print("STEP 4: Expansions Menu")
        print("=" * 60)
        print("\nWe need to:")
        print("  - Find Expansions button")
        print("  - Calibrate A/B series buttons")
        print("  - Calibrate expansion scroll and slots")
        
        # First click a difficulty to enter it
        if "difficulty_buttons" in self.config and "beginner" in self.config["difficulty_buttons"]:
            print("\nEntering Beginner difficulty...")
            self.controller.tap(*self.config["difficulty_buttons"]["beginner"])
            time.sleep(3)
        
        input("\nPress ENTER when inside a difficulty (seeing battle list)...")
        
        # Expansions button
        exp_button = self.calibrate_with_verification(
            "Calibration - Expansions",
            "📍 RIGHT CLICK on EXPANSIONS button/tab",
            "Expansions button"
        )
        
        if exp_button:
            self.config["expansions_button"] = list(exp_button)
            
            print("\nOpening Expansions menu...")
            self.controller.tap(*exp_button)
            time.sleep(2)
    
    def step_series_buttons(self):
        """Step 5: A/B series buttons"""
        print("\n" + "=" * 60)
        print("STEP 5: Series Buttons (A/B)")
        print("=" * 60)
        
        input("\nPress ENTER when Expansions menu is open...")
        
        series = {}
        
        # B first (it's usually selected by default or easy to see)
        b_pos = self.calibrate_with_verification(
            "Calibration - B Series",
            "📍 RIGHT CLICK on B-SERIES button",
            "B-series button"
        )
        if b_pos:
            series["B"] = list(b_pos)
        
        # A series
        a_pos = self.calibrate_with_verification(
            "Calibration - A Series",
            "📍 RIGHT CLICK on A-SERIES button",
            "A-series button"
        )
        if a_pos:
            series["A"] = list(a_pos)
        
        if series:
            self.config["series_buttons"] = series
            print("✓ Series buttons calibrated")
    
    def step_expansion_navigation(self):
        """Step 6: Expansion scroll and slots"""
        print("\n" + "=" * 60)
        print("STEP 6: Expansion Navigation")
        print("=" * 60)
        
        input("\nPress ENTER when viewing expansion list...")
        
        # Scroll gesture
        print("\n--- Expansion Scroll Gesture ---")
        print("This scrolls through the expansion list")
        
        scroll_start = self.get_point_from_click(
            "Expansion Scroll START",
            "📍 RIGHT CLICK where scroll should START (bottom of list)"
        )
        
        scroll_end = self.get_point_from_click(
            "Expansion Scroll END",
            "📍 RIGHT CLICK where scroll should END (top of list)"
        )
        
        if scroll_start and scroll_end:
            self.config["expansion_scroll"] = {
                "start": list(scroll_start),
                "end": list(scroll_end)
            }
            
            print("\nTesting expansion scroll...")
            self.controller.swipe_with_hold(*scroll_start, *scroll_end, duration=400, hold_time=1000, delay=1.2)
            
            response = input("Did it scroll ONE expansion? (y/n): ").lower()
            if response != 'y':
                print("⚠️ You may need to adjust this later")
        
        # Expansion slots
        print("\n--- Expansion Card Slots ---")
        print("Calibrate 3 expansion card positions (top, middle, bottom)")
        
        slots = []
        for i, position in enumerate(["TOP", "MIDDLE", "BOTTOM"], 1):
            pos = self.calibrate_with_verification(
                f"Expansion Slot {i}",
                f"📍 RIGHT CLICK on the {position} expansion card",
                f"{position} expansion slot"
            )
            if pos:
                slots.append(list(pos))
        
        if slots:
            self.config["expansion_slots"] = slots
            print("✓ Expansion slots calibrated")
    
    def step_battle_ui(self):
        """Step 7: Battle UI (AUTO and BATTLE buttons)"""
        print("\n" + "=" * 60)
        print("STEP 7: Battle UI")
        print("=" * 60)
        print("\nWe need to calibrate AUTO and BATTLE buttons")
        print("You need to start a battle for this")
        
        input("\nPress ENTER when in a battle (AUTO and BATTLE visible)...")
        
        # AUTO button
        auto_pos = self.calibrate_with_verification(
            "Calibration - AUTO",
            "📍 RIGHT CLICK on the AUTO button",
            "AUTO button"
        )
        if auto_pos:
            self.config["auto_button"] = list(auto_pos)
        
        # BATTLE button
        battle_pos = self.calibrate_with_verification(
            "Calibration - BATTLE",
            "📍 RIGHT CLICK on the BATTLE button",
            "BATTLE button"
        )
        if battle_pos:
            self.config["battle_button"] = list(battle_pos)
        
        print("✓ Battle UI calibrated")
    
    def step_battle_list_region(self):
        """Step 8: Battle list detection region"""
        print("\n" + "=" * 60)
        print("STEP 8: Battle List Region")
        print("=" * 60)
        print("\nThis defines where to look for battles with rewards")
        
        input("\nPress ENTER when viewing a battle list...")
        
        self.current_screenshot = self.controller.screenshot_cv()
        self.current_screenshot_display = cv2.resize(
            self.current_screenshot, 
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_AREA
        )
        
        points = []
        display = self.current_screenshot_display.copy()
        
        def region_callback(event, x, y, flags, param):
            if event == cv2.EVENT_RBUTTONDOWN:
                # Convert to actual coordinates
                actual_x = int(x / self.display_scale)
                actual_y = int(y / self.display_scale)
                points.append((actual_x, actual_y))
                print(f"  ✓ Point {len(points)}: ({actual_x}, {actual_y})")
                cv2.circle(display, (x, y), 5, (0, 0, 255), -1)
                if len(points) == 2:
                    # Draw rectangle using display coordinates
                    p1_display = (int(points[0][0] * self.display_scale), int(points[0][1] * self.display_scale))
                    p2_display = (x, y)
                    cv2.rectangle(display, p1_display, p2_display, (0, 255, 0), 2)
                cv2.imshow("Battle List Region", display)
        
        cv2.namedWindow("Battle List Region")
        cv2.setMouseCallback("Battle List Region", region_callback)
        cv2.imshow("Battle List Region", display)
        
        print("\n📍 RIGHT CLICK on TOP-LEFT corner of battle list area")
        while len(points) < 1:
            cv2.waitKey(1)
        
        print("📍 RIGHT CLICK on BOTTOM-RIGHT corner of battle list area")
        while len(points) < 2:
            cv2.waitKey(1)
        
        print("\nPress SPACE to confirm")
        while True:
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break
        
        cv2.destroyAllWindows()
        
        x1, y1 = points[0]
        x2, y2 = points[1]
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        self.config["battle_list_region"] = [x, y, w, h]
        print(f"✓ Battle list region: x={x}, y={y}, w={w}, h={h}")
    
    def step_reward_detection_region(self):
        """Step 9: Reward detection region"""
        print("\n" + "=" * 60)
        print("STEP 9: Reward Detection Region")
        print("=" * 60)
        print("\nThis is where reward icons appear (RIGHT side of battle cards)")
        
        input("\nPress ENTER when viewing battles with REWARD ICONS visible...")
        
        self.current_screenshot = self.controller.screenshot_cv()
        self.current_screenshot_display = cv2.resize(
            self.current_screenshot, 
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_AREA
        )
        
        points = []
        display = self.current_screenshot_display.copy()
        
        def region_callback(event, x, y, flags, param):
            if event == cv2.EVENT_RBUTTONDOWN:
                # Convert to actual coordinates
                actual_x = int(x / self.display_scale)
                actual_y = int(y / self.display_scale)
                points.append((actual_x, actual_y))
                print(f"  ✓ Point {len(points)}: ({actual_x}, {actual_y})")
                cv2.circle(display, (x, y), 5, (0, 0, 255), -1)
                if len(points) == 2:
                    # Draw rectangle using display coordinates
                    p1_display = (int(points[0][0] * self.display_scale), int(points[0][1] * self.display_scale))
                    p2_display = (x, y)
                    cv2.rectangle(display, p1_display, p2_display, (0, 255, 0), 2)
                cv2.imshow("Reward Region", display)
        
        cv2.namedWindow("Reward Region")
        cv2.setMouseCallback("Reward Region", region_callback)
        cv2.imshow("Reward Region", display)
        
        print("\n📍 RIGHT CLICK on TOP-LEFT of reward icon area")
        while len(points) < 1:
            cv2.waitKey(1)
        
        print("📍 RIGHT CLICK on BOTTOM-RIGHT of reward icon area")
        while len(points) < 2:
            cv2.waitKey(1)
        
        print("\nPress SPACE to confirm")
        while True:
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break
        
        cv2.destroyAllWindows()
        
        x1, y1 = points[0]
        x2, y2 = points[1]
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        self.config["reward_detection_region"] = [x, y, w, h]
        print(f"✓ Reward detection region: x={x}, y={y}, w={w}, h={h}")
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"\n✓ Configuration saved: {self.config_file}")
    
    def run_full_calibration(self):
        """Run complete calibration"""
        print("\n" + "=" * 60)
        print(f"FULL CALIBRATION - Device: {self.device_id}")
        print("=" * 60)
        print(f"\nConfig will be saved to: {self.config_file}")
        print("\nSteps:")
        print("  0. App icon (home screen)")
        print("  1. Battles tab")
        print("  2. Solo Battle button")
        print("  3. Difficulty buttons")
        print("  4. Expansions menu")
        print("  5. Series buttons (A/B)")
        print("  6. Expansion navigation")
        print("  7. Battle UI (AUTO/BATTLE)")
        print("  8. Battle list region")
        print("  9. Reward detection region")
        
        input("\nPress ENTER to begin...")
        
        self.step_app_icon()
        self.step_battles_tab()
        self.step_solo_battle()
        self.step_difficulty_buttons()
        self.step_expansions_menu()
        self.step_series_buttons()
        self.step_expansion_navigation()
        self.step_battle_ui()
        self.step_battle_list_region()
        self.step_reward_detection_region()
        
        self.save_config()
        
        print("\n" + "=" * 60)
        print("CALIBRATION COMPLETE!")
        print("=" * 60)
        print(f"\nSaved to: {self.config_file}")
        print("\nCalibrated items:")
        for key in self.config:
            print(f"  ✓ {key}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("  1. Test with: python test_05_adb_full_workflow.py")
        print("  2. If working, test parallelization")


def main():
    print("=" * 60)
    print("IMPROVED CALIBRATION TOOL")
    print("=" * 60)
    
    # Check for devices
    devices = ADBController.get_all_devices()
    
    if not devices:
        print("\n❌ No devices found!")
        print("Make sure MuMu Player is running and connected via ADB")
        return
    
    print(f"\nFound {len(devices)} device(s):")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # Device selection
    if len(devices) == 1:
        selected = devices[0]
    else:
        choice = input(f"\nSelect device (1-{len(devices)}) or ENTER for first: ").strip()
        if choice:
            idx = int(choice) - 1
            selected = devices[idx]
        else:
            selected = devices[0]
    
    print(f"\n✓ Selected device: {selected}")
    
    # Config type selection
    if len(devices) > 1:
        print("\nConfig file option:")
        print("  1. Shared config (adb_config.json) - if all emulators same resolution")
        print("  2. Device-specific config - for different resolutions")
        
        config_choice = input("Select (1/2) or ENTER for shared: ").strip()
        use_device_specific = (config_choice == "2")
    else:
        use_device_specific = False
    
    # Run calibration
    calibrator = ImprovedCalibrator(selected, use_device_specific)
    calibrator.run_full_calibration()


if __name__ == "__main__":
    main()