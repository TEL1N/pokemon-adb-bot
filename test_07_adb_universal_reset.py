#!/usr/bin/env python3
"""
TEST 07: Universal Reset (ADB Version)
Resets game to Intermediate Battle screen
"""

import time
from adb_controller import ADBController


class UniversalResetADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)
    
    def run_universal_reset(self):
        """
        Universal reset flow to get back to Intermediate battle screen
        """
        print("\n--- Executing Universal Reset Flow ---")
        time.sleep(2)
        
        # Step 1: Press BACK 30 times to ensure all menus closed
        print("Pressing BACK 30 times to close all menus...")
        for i in range(30):
            self.controller.press_back(delay=0.3)
            print(f"BACK {i+1}/30", end="\r")
        print("\n✓ All menus closed")
        
        # Small delay
        time.sleep(1)
        
        # Step 2: Navigate to battles
        # Click main Pokemon app (if needed - may not be necessary in emulator)
        # Skip this step for now
        
        # Step 3: Click Battles tab
        print("\nClicking BATTLES tab...")
        # We'll need coordinates from config
        try:
            import json
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
            
            battles_tab = tuple(config.get("battles_tab", (0, 0)))
            self.controller.tap(*battles_tab)
            time.sleep(1)
            
            # Step 4: Click Solo Battle
            solo_battle = tuple(config.get("solo_battle_button", (0, 0)))
            print("Clicking SOLO BATTLE...")
            self.controller.tap(*solo_battle)
            time.sleep(1)
            
            # Step 5: Scroll twice to reveal Intermediate
            print("Scrolling to reveal difficulties...")
            scroll_config = config.get("difficulty_scroll", {})
            start = tuple(scroll_config.get("start", (0, 0)))
            end = tuple(scroll_config.get("end", (0, 0)))
            
            for i in range(2):
                print(f"Scroll {i+1}/2")
                self.controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1)
            
            # Step 6: Click Intermediate
            difficulty_buttons = config.get("difficulty_buttons", {})
            intermediate = tuple(difficulty_buttons.get("intermediate", (0, 0)))
            print("Clicking INTERMEDIATE...")
            self.controller.tap(*intermediate)
            time.sleep(1)
            
            print("\n✓ Universal Reset Flow completed")
            
        except Exception as e:
            print(f"\n✗ Reset flow failed: {e}")
            print("Make sure adb_config.json has all required coordinates")


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 07: UNIVERSAL RESET")
    print("="*60)
    
    print("\nThis will reset the game to Intermediate battle screen")
    print("Use this after completing a battle")
    
    input("\nPress ENTER to start reset...")
    
    resetter = UniversalResetADB()
    resetter.run_universal_reset()


if __name__ == "__main__":
    main()