#!/usr/bin/env python3
"""
TEST 07: Universal Reset (ADB Version)
Resets game to Intermediate Battle screen
WITH GENEROUS DELAYS to ensure everything loads properly
"""

import time
from adb_controller import ADBController


class UniversalResetADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)
    
    def run_universal_reset(self):
        """
        Universal reset flow to get back to Intermediate battle screen
        Uses 10-second delays between major actions to ensure loading
        """
        print("\n--- Executing Universal Reset Flow (SLOW & SAFE) ---")
        time.sleep(2)
        
        # Step 1: Press BACK 30 times to ensure all menus closed
        print("\n[Step 1/7] Pressing BACK 70 times to close all menus...")
        for i in range(70):
            self.controller.press_back(delay=0.3)
            if (i + 1) % 10 == 0:
                print(f"  BACK {i+1}/70")
        print("✓ All menus closed")
        
        """
        # Generous delay
        print("  Waiting 10 seconds...")
        time.sleep(10)
       
        # Step 2: Press HOME to go to home screen
        print("\n[Step 2/7] Pressing HOME button...")
        self.controller.press_home(delay=2)
        print("✓ On home screen")
        
        # Generous delay
        print("  Waiting 10 seconds...")
        time.sleep(10)
         """
        try:
            import json
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
            
            # Step 3: Click Pokemon TCG app icon
            print("\n[Step 3/7] Clicking Pokemon TCG app icon...")
            app_icon = tuple(config.get("pokemon_app_icon", (0, 0)))
            if app_icon != (0, 0):
                self.controller.tap(*app_icon)
                print("✓ App icon clicked")
            else:
                print("⚠️ App icon not calibrated, skipping...")
            
            # Wait for app to fully load
            print("  Waiting 5 seconds for app to load...")
            time.sleep(5)
            
            # Step 4: Click Battles tab
            print("\n[Step 4/7] Clicking BATTLES tab...")
            battles_tab = tuple(config.get("battles_tab", (0, 0)))
            self.controller.tap(*battles_tab)
            print("✓ Battles tab clicked")
            
            # Wait for battles screen to load
            print("  Waiting 5 seconds...")
            time.sleep(5)
            
            # Step 5: Click Solo Battle
            print("\n[Step 5/7] Clicking SOLO BATTLE...")
            solo_battle = tuple(config.get("solo_battle_button", (0, 0)))
            self.controller.tap(*solo_battle)
            print("✓ Solo Battle clicked")
            
            # Wait for solo battle screen to load
            print("  Waiting 5 seconds...")
            time.sleep(5)
            
            # Step 6: Scroll twice to reveal Intermediate
            print("\n[Step 6/7] Scrolling to reveal difficulties...")
            scroll_config = config.get("difficulty_scroll", {})
            start = tuple(scroll_config.get("start", (0, 0)))
            end = tuple(scroll_config.get("end", (0, 0)))
            
            for i in range(1):
                print(f"  Scroll {i+1}/2")
                self.controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1)
                time.sleep(2)  # Extra delay between scrolls
            
            print("✓ Scrolled to reveal difficulties")
            
            # Wait after scrolling
            print("  Waiting 5 seconds...")
            time.sleep(5)
            
            # Step 7: Click Intermediate
            print("\n[Step 7/7] Clicking INTERMEDIATE...")
            difficulty_buttons = config.get("difficulty_buttons", {})
            intermediate = tuple(difficulty_buttons.get("intermediate", (0, 0)))
            self.controller.tap(*intermediate)
            print("✓ Intermediate clicked")
            
            # Final delay to ensure we're ready
            print("  Waiting 3 seconds for final load...")
            time.sleep(3)
            
            print("\n" + "="*60)
            print("✓ UNIVERSAL RESET FLOW COMPLETED")
            print("="*60)
            print("Game should now be at Intermediate battle screen")
            
        except Exception as e:
            print(f"\n✗ Reset flow failed: {e}")
            print("Make sure adb_config.json has all required coordinates")
            raise


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 07: UNIVERSAL RESET")
    print("="*60)
    
    print("\nThis will reset the game to Intermediate battle screen")

    
    input("\nPress ENTER to start reset...")
    
    resetter = UniversalResetADB()
    resetter.run_universal_reset()


if __name__ == "__main__":
    main()