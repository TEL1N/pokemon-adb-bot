#!/usr/bin/env python3
"""
TEST 07: Universal Reset (ADB Version)
Resets game to Intermediate Battle screen
WITH GENEROUS DELAYS to ensure everything loads properly
"""

import time
from adb_controller import ADBController


class UniversalResetADB:
    # CHANGE THIS LINE:
    def __init__(self, device_id=None):
        self.adb = ADBController(device_id)
        # ... rest of the code ...
        self.controller = ADBController(device_id)
    
    def run_universal_reset(self):
        """
        Universal reset flow to get back to Beginner battle screen
        Uses generous delays between major actions to ensure loading
        """
        print("\n--- Executing Universal Reset Flow (SLOW & SAFE) ---")
        time.sleep(2)
        
        # Step 1: Press BACK 70 times to ensure all menus closed
        print("\n[Step 1/6] Pressing BACK 70 times to close all menus...")
        for i in range(70):
            self.controller.press_back(delay=0.3)
            if (i + 1) % 10 == 0:
                print(f"  BACK {i+1}/70")
        print("✓ All menus closed")
        
        try:
            import json
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
            
            # Step 2: Click Pokemon TCG app icon
            print("\n[Step 2/6] Clicking Pokemon TCG app icon...")
            app_icon = tuple(config.get("pokemon_app_icon", (0, 0)))
            if app_icon != (0, 0):
                self.controller.tap(*app_icon)
                print("✓ App icon clicked")
            else:
                print("⚠️ App icon not calibrated, skipping...")
            
            # Wait for app to fully load
            print("  Waiting 5 seconds for app to load...")
            time.sleep(5)
            
            # Step 3: Click Battles tab
            print("\n[Step 3/6] Clicking BATTLES tab...")
            battles_tab = tuple(config.get("battles_tab", (0, 0)))
            self.controller.tap(*battles_tab)
            print("✓ Battles tab clicked")
            
            # Wait for battles screen to load
            print("  Waiting 5 seconds...")
            time.sleep(5)
            
            # Step 4: Click Solo Battle
            print("\n[Step 4/6] Clicking SOLO BATTLE...")
            solo_battle = tuple(config.get("solo_battle_button", (0, 0)))
            self.controller.tap(*solo_battle)
            print("✓ Solo Battle clicked")
            
            # Wait for solo battle screen to load
            print("  Waiting 5 seconds...")
            time.sleep(5)
            
            # Step 5: NO SCROLL - Beginner is already visible!
            print("\n[Step 5/6] Beginner difficulty already visible (no scroll needed)")
            print("✓ Ready to click Beginner")
            
            # Wait after "scrolling" (keeping timing consistent)
            print("  Waiting 3 seconds...")
            time.sleep(3)
            
            # Step 6: Click Beginner
            print("\n[Step 6/6] Clicking BEGINNER...")
            difficulty_buttons = config.get("difficulty_buttons", {})
            beginner = tuple(difficulty_buttons.get("beginner", (0, 0)))
            self.controller.tap(*beginner)
            print("✓ Beginner clicked")
            
            # Final delay to ensure we're ready
            print("  Waiting 3 seconds for final load...")
            time.sleep(3)
            
            print("\n" + "="*60)
            print("✓ UNIVERSAL RESET FLOW COMPLETED")
            print("="*60)
            print("Game should now be at Beginner battle screen")
            
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