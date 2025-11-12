#!/usr/bin/env python3
"""
TEST 03: Find Battles with Rewards (ADB Version)
Tests reward icon detection and battle finding using ADB screenshots
"""

import cv2
import numpy as np
import time
import json
from adb_controller import ADBController


class BattleFinderADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)
        self.battle_list_region = None
        
        # Load config
        self.config = self.load_config()
        
        # NEW: Load reward detection region
        if 'reward_detection_region' in self.config:
            self.reward_detection_region = tuple(self.config['reward_detection_region'])
            print(f"✓ Loaded reward detection region: {self.reward_detection_region}")
        else:
            self.reward_detection_region = None
            print("⚠️ No reward detection region configured")
    
    def load_config(self):
        """Load calibrated coordinates"""
        try:
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
                print("✓ Loaded calibration config")
                return config
        except:
            print("⚠️  No config found, run test_02 first")
            return {}
    
    def take_screenshot(self):
        """Take screenshot via ADB and return OpenCV format"""
        return self.controller.screenshot_cv()
    
    def calibrate_battle_list_region(self):
        """
        Define the app window region to search for battles
        Since we're in emulator, we can use full screen or define a region
        """
        print("\n" + "="*60)
        print("CALIBRATION: Battle List Region")
        print("="*60)
        print("\nFor emulator, we can use the full screen.")
        print("Or you can define a specific region to search.")
        
        use_full = input("\nUse full emulator screen? (y/n): ").lower()
        
        if use_full == 'y':
            width, height = self.controller.get_screen_size()
            self.battle_list_region = (0, 0, width, height)
            print(f"✓ Using full screen: {self.battle_list_region}")
        else:
            print("\nTake a screenshot, then RIGHT CLICK on:")
            print("  1. Top-left corner of battle list area")
            print("  2. Bottom-right corner of battle list area")
            
            # Use OpenCV to get region
            screenshot = self.take_screenshot()
            
            points = []
            
            def mouse_callback(event, x, y, flags, param):
                if event == cv2.EVENT_RBUTTONDOWN:
                    points.append((x, y))
                    print(f"  ✓ Point {len(points)}: ({x}, {y})")
                    cv2.circle(screenshot, (x, y), 5, (0, 0, 255), -1)
                    cv2.imshow("Battle List Region", screenshot)
                    
                    if len(points) == 2:
                        cv2.destroyAllWindows()
            
            cv2.namedWindow("Battle List Region")
            cv2.setMouseCallback("Battle List Region", mouse_callback)
            cv2.imshow("Battle List Region", screenshot)
            
            print("RIGHT CLICK on top-left corner...")
            while len(points) < 1:
                cv2.waitKey(1)
            
            print("RIGHT CLICK on bottom-right corner...")
            while len(points) < 2:
                cv2.waitKey(1)
            
            x1, y1 = points[0]
            x2, y2 = points[1]
            
            self.battle_list_region = (x1, y1, x2 - x1, y2 - y1)
            print(f"✓ Battle list region: {self.battle_list_region}")
        
        # Save to config
        self.config['battle_list_region'] = list(self.battle_list_region)
        with open('adb_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        return True
    
    def find_reward_icons(self, screen_cv):
        """
        Find reward icons using calibrated detection region
        Returns list of (x, y, area) tuples in FULL SCREEN coordinates
        """
        if not self.reward_detection_region:
            print("  ⚠️ No reward detection region calibrated!")
            return []
        
        x, y, w, h = self.reward_detection_region
        
        # Crop to reward region only
        cropped = screen_cv[y:y+h, x:x+w]
        
        # Convert to HSV
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
        
        # Simplified, more lenient color ranges
        color_ranges = [
            # Cyan/Blue (magnifying glass, hourglass)
            ([80, 100, 150], [130, 255, 255]),
            
            # Purple/Magenta (hourglass)
            ([130, 100, 150], [170, 255, 255]),
            
            # Yellow/Gold
            ([15, 100, 150], [45, 255, 255]),
            
            # Any bright saturated color (catch-all)
            ([0, 120, 180], [180, 255, 255])
        ]
        
        # Combine all color masks
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in color_ranges:
            lower_np = np.array(lower)
            upper_np = np.array(upper)
            mask = cv2.inRange(hsv, lower_np, upper_np)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # More lenient size filter
            if 150 < area < 3000:
                bx, by, bw, bh = cv2.boundingRect(contour)
                
                # Convert to FULL SCREEN coordinates
                center_x = x + bx + bw // 2
                center_y = y + by + bh // 2
                
                # Aspect ratio check (still useful)
                aspect_ratio = bw / bh if bh > 0 else 0
                if 0.5 < aspect_ratio < 2.5:
                    detections.append((center_x, center_y, area))
        
        return detections
    
    def verify_detection(self, click_pos, max_attempts=2):
        """
        Double-check detection by waiting and re-scanning
        Returns verified position or None if false positive
        """
        print("  🔍 Verifying detection...")
        
        for attempt in range(max_attempts):
            time.sleep(1.0)  # Wait for screen to settle
            
            # Take fresh screenshot
            recheck_pos = self.find_battle_with_rewards()
            
            if not recheck_pos:
                print(f"  ✗ Verification {attempt+1}/{max_attempts}: Not detected")
                continue
            
            # Check if positions are similar (within 50px)
            x1, y1 = click_pos
            x2, y2 = recheck_pos
            
            distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            
            if distance > 50:
                print(f"  ✗ Verification {attempt+1}/{max_attempts}: Position changed ({distance:.0f}px)")
                continue
            
            print(f"  ✓ Verification {attempt+1}/{max_attempts}: CONFIRMED")
            return recheck_pos
        
        print("  ✗ Detection failed verification - FALSE POSITIVE")
        return None
    
    def filter_to_battle_list(self, detections):
        """
        Filter detections - but since we're using a calibrated region,
        this is mostly a pass-through now
        """
        # Already filtered by using calibrated region
        return detections
    
    def group_icons_into_battles(self, icons):
        """Group nearby icons (same battle card)"""
        if not icons:
            return []
        
        # Sort by Y coordinate
        icons = sorted(icons, key=lambda p: p[1])
        
        clusters = []
        current_cluster = [icons[0]]
        
        for i in range(1, len(icons)):
            y_diff = abs(icons[i][1] - current_cluster[-1][1])
            
            # Icons within 80px = same battle
            if y_diff < 80:
                current_cluster.append(icons[i])
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [icons[i]]
        
        if len(current_cluster) >= 2:
            clusters.append(current_cluster)
        
        return clusters
    
    def get_battle_click_position(self, cluster):
        """
        Calculate where to click for a battle
        Since rewards are on the right, click DIRECTLY on the reward area
        """
        # Average position of all icons in cluster
        avg_x = sum(p[0] for p in cluster) // len(cluster)
        avg_y = sum(p[1] for p in cluster) // len(cluster)
        
        # Click directly on the reward area (battle card extends left from here)
        # The reward icons ARE on the battle card, so clicking them works
        click_x = avg_x
        click_y = avg_y
        
        return (click_x, click_y)
    
    def find_battle_with_rewards(self):
        """
        Main function: Find a battle with rewards on current screen
        Returns (click_x, click_y) or None
        """
        print("\n--- Scanning for battles with rewards ---")
        
        # Take screenshot via ADB
        screen_cv = self.take_screenshot()
        
        # Find reward icons
        all_icons = self.find_reward_icons(screen_cv)
        print(f"  Found {len(all_icons)} reward icon(s) on screen")
        
        # Filter to battle list region
        filtered_icons = self.filter_to_battle_list(all_icons)
        print(f"  Filtered to {len(filtered_icons)} icon(s) in battle list")
        
        if not filtered_icons:
            print("  ✗ No reward icons found")
            return None
        
        # Group into battles
        battle_clusters = self.group_icons_into_battles(filtered_icons)
        print(f"  Grouped into {len(battle_clusters)} battle(s) with rewards")
        
        if not battle_clusters:
            print("  ✗ No valid battles (need 2+ icons per battle)")
            return None
        
        # Get first battle
        first_battle = battle_clusters[0]
        click_pos = self.get_battle_click_position(first_battle)
        
        print(f"  ✓ Found battle with {len(first_battle)} reward icons")
        print(f"  Will click at: ({click_pos[0]}, {click_pos[1]})")
        
        return click_pos
    
    def show_detection_visually(self, click_pos):
        """Tap in emulator to show detection"""
        if not click_pos:
            return
        
        print("\n--- Visual Confirmation ---")
        print("  Tapping battle card position in emulator...")
        
        click_x, click_y = click_pos
        
        # Only tap the battle card position (removed reward area tap)
        print(f"  Tapping battle card at ({click_x}, {click_y})")
        self.controller.tap(click_x, click_y, delay=0.5)
        time.sleep(1.5)
        
        print("\n  Did it highlight the correct battle card? (y/n)")
    
    def drag_scroll_down(self, distance=200):
        """Scroll down in battle list with hold"""
        if not self.battle_list_region:
            width, height = self.controller.get_screen_size()
            scroll_x = width // 2
            scroll_y = height // 2
        else:
            x, y, w, h = self.battle_list_region
            scroll_x = x + w // 2
            scroll_y = y + int(h * 0.5)
        
        print(f"  Scrolling down at ({scroll_x}, {scroll_y})...")
        # Use swipe_with_hold to prevent flick
        self.controller.swipe_with_hold(
            scroll_x, scroll_y, 
            scroll_x, scroll_y + distance, 
            duration=400, hold_time=1000, delay=0.8
        )

    def drag_scroll_up(self, distance=200):
        """Scroll up in battle list with hold"""
        if not self.battle_list_region:
            width, height = self.controller.get_screen_size()
            scroll_x = width // 2
            scroll_y = height // 2
        else:
            x, y, w, h = self.battle_list_region
            scroll_x = x + w // 2
            scroll_y = y + int(h * 0.5)
        
        print(f"  Scrolling up at ({scroll_x}, {scroll_y})...")
        # Use swipe_with_hold to prevent flick
        self.controller.swipe_with_hold(
            scroll_x, scroll_y, 
            scroll_x, scroll_y - distance, 
            duration=400, hold_time=1000, delay=0.8
        )
    
    def search_all_battles(self):
        """Scroll through battle list to find rewards"""
        print("\n" + "="*60)
        print("SEARCHING ALL BATTLES")
        print("="*60)
        
        # Scroll to top first
        print("\nScrolling to top of battle list...")
        for i in range(3):
            print(f"  Scroll up {i+1}/3")
            self.drag_scroll_up(distance=200)
            time.sleep(0.5)
        
        print("✓ At top of list\n")
        
        # Scan while scrolling down
        max_scrolls = 6
        
        for scroll_num in range(max_scrolls + 1):
            print(f"\nPosition {scroll_num + 1}/{max_scrolls + 1}:")
            
            # Check current view
            battle_pos = self.find_battle_with_rewards()

            if battle_pos:
                # Verify it's not a false positive
                verified_pos = self.verify_detection(battle_pos)
                if verified_pos:
                    print(f"\n✓ FOUND verified battle with rewards!")
                    return verified_pos
                else:
                    print("  False positive detected, continuing search...")
                    # Continue to next scroll position
            
            # Scroll down (except on last check)
            if scroll_num < max_scrolls:
                print(f"  No rewards here, scrolling down...")
                self.drag_scroll_down(distance=200)
                time.sleep(0.8)
        
        print("\n✗ No battles with rewards found in entire list")
        return None


def test_calibration():
    """Test: Calibrate battle list region"""
    print("="*60)
    print("TEST: Calibrate Battle List Region")
    print("="*60)
    
    print("\nMake sure you're on a screen showing battles")
    input("Press ENTER when ready...")
    
    finder = BattleFinderADB()
    
    if finder.calibrate_battle_list_region():
        print("\n✓ Calibration successful!")
    else:
        print("\n✗ Calibration failed")


def test_single_detection():
    """Test: Detect battles on current screen"""
    print("="*60)
    print("TEST: Detect Battles (Current Screen)")
    print("="*60)
    
    print("\nMake sure you're on a screen showing battles")
    input("Press ENTER when ready...")
    
    finder = BattleFinderADB()
    
    # Load region if exists
    if 'battle_list_region' in finder.config:
        finder.battle_list_region = tuple(finder.config['battle_list_region'])
        print(f"✓ Loaded battle list region: {finder.battle_list_region}")
    else:
        print("⚠️  No saved region, run Test 1 first")
        return
    
    # Find battle
    battle_pos = finder.find_battle_with_rewards()
    
    if battle_pos:
        print("\n" + "="*60)
        print("SUCCESS - Battle Found!")
        print("="*60)
        
        # Show visually
        finder.show_detection_visually(battle_pos)
        
        response = input("\nWas the detection correct? (y/n): ").lower()
        if response == 'y':
            print("✓ Detection working correctly!")
        else:
            print("✗ Detection needs adjustment")
    else:
        print("\n✗ No battles with rewards found")


def test_scroll_and_search():
    """Test: Scroll through entire list"""
    print("="*60)
    print("TEST: Scroll Through All Battles")
    print("="*60)
    
    print("\nMake sure you're on a screen showing battles")
    input("Press ENTER when ready...")
    
    finder = BattleFinderADB()
    
    # Load region
    if 'battle_list_region' in finder.config:
        finder.battle_list_region = tuple(finder.config['battle_list_region'])
        print(f"✓ Loaded battle list region")
    else:
        print("⚠️  No saved region, run Test 1 first")
        return
    
    # Search
    battle_pos = finder.search_all_battles()
    
    if battle_pos:
        print("\n" + "="*60)
        print("SUCCESS - Battle Found!")
        print("="*60)
        
        # Show visually
        finder.show_detection_visually(battle_pos)
        
        response = input("\nWas the detection correct? (y/n): ").lower()
        if response == 'y':
            print("✓ Full search working correctly!")
        else:
            print("✗ Detection needs adjustment")
    else:
        print("\n✗ No battles with rewards in entire list")


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 03: FIND BATTLES")
    print("="*60)
    
    print("\nTests Available:")
    print("  1. Calibrate Battle List Region")
    print("  2. Test Detection (current screen)")
    print("  3. Test Scroll & Search (full list)")
    print("  4. Run All Tests")
    
    choice = input("\nSelect test (1-4): ").strip()
    
    if choice == "1":
        test_calibration()
    elif choice == "2":
        test_single_detection()
    elif choice == "3":
        test_scroll_and_search()
    elif choice == "4":
        print("\n--- Running All Tests ---\n")
        test_calibration()
        print("\n\n")
        input("Press ENTER for next test...")
        test_single_detection()
        print("\n\n")
        input("Press ENTER for next test...")
        test_scroll_and_search()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()