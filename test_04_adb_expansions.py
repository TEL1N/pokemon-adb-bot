#!/usr/bin/env python3
"""
TEST 04: Expansion Navigation (ADB Version)
Searches through expansion packs when no rewards on main screen
"""

import json
import time
from adb_controller import ADBController
from test_03_adb_find_battles import BattleFinderADB

# Max down-scrolls inside a single expansion
MAX_DOWN_SCANS_PER_EXPANSION = 9


class ExpansionSearcherADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)  # Auto-detect if None
        self.finder = BattleFinderADB(device_id)    # Auto-detect if None
        self.config = self.load_config()
        self.checked_expansions = set()
        self.max_expansions = 12  # Adjust if needed
    
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
    
    # ==================== BASIC ACTIONS ====================
    
    def click_expansions_button(self):
        """Open expansions menu"""
        pos = tuple(self.config.get("expansions_button", (0, 0)))
        print(f"\nClicking Expansions button at {pos}...")
        self.controller.tap(*pos)
        time.sleep(2)
    
    def perform_scroll_gesture(self, times=1):
        """Perform calibrated scroll gesture in expansion list with hold"""
        scroll_config = self.config.get("expansion_scroll", {})
        start = tuple(scroll_config.get("start", (0, 0)))
        end = tuple(scroll_config.get("end", (0, 0)))
        
        for i in range(times):
            print(f"  ↕ Expansion scroll gesture {i+1}/{times}")
            # Swipe 400ms + hold 1000ms = 1400ms total
            self.controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1.2)
            time.sleep(0.5)
    
    def open_visible_expansion(self, visible_index):
        """Click the nth visible expansion slot"""
        slots = self.config.get("expansion_slots", [])
        if visible_index >= len(slots):
            print(f"✗ Invalid slot index: {visible_index}")
            return False
        
        pos = tuple(slots[visible_index])
        print(f"Opening expansion slot {visible_index + 1} at {pos}...")
        self.controller.tap(*pos)
        time.sleep(3)
        return True
    
    def switch_series(self, series_name):
        """Switch to A or B series"""
        series_buttons = self.config.get("series_buttons", {})
        pos = tuple(series_buttons.get(series_name, (0, 0)))
        
        print(f"Switching to {series_name}-series at {pos}...")
        self.controller.tap(*pos)
        time.sleep(1.5)
    
    # ==================== LOGIC ====================
    
    def get_scrolls_for_expansion(self, index):
        """How many menu scrolls needed before clicking expansion N"""
        if index <= 2:
            return 0
        return index - 2
    
    def get_visible_slot_index(self, expansion_number):
        """
        Which slot to click for expansion N
        First expansion = slot #2 (index 1)
        Second expansion = slot #3 (index 2)
        3+ = bottom slot (index 2)
        """
        if expansion_number == 1:
            return 1  # slot #2
        elif expansion_number == 2:
            return 2  # slot #3
        else:
            return 2  # always bottom slot after scrolling
    
    def scan_expansion_for_rewards(self):
        """
        Scan inside an expansion for battles with rewards
        OPTIMIZED: Just scroll to bottom fast (where rewards are) and check once
        
        Returns (x, y) click position if found, else None
        """
        print("  Scanning expansion for rewards...")
        
        # Get battle list scroll region from config
        battle_list_region = self.config.get("battle_list_region", None)
        if not battle_list_region:
            print("  ⚠️ Battle list region not calibrated!")
            return None
        
        x, y, w, h = battle_list_region
        
        # Calculate scroll coordinates INSIDE the battle list
        start_x = x + w // 2
        start_y = y + int(h * 0.8)  # Bottom of list
        end_x = start_x
        end_y = y + int(h * 0.2)    # Top of list
        
        # OPTIMIZATION: 3 fast scrolls to bottom (no hold, pure speed)
        print("  Fast scrolling to bottom (where rewards are)...")
        for i in range(3):
            print(f"    Quick scroll {i+1}/3", end="\r")
            self.controller.swipe(
                start_x, start_y,
                end_x, end_y,
                duration=200  # FAST! No hold time
            )
            time.sleep(0.2)  # Tiny delay between scrolls
        
        print("\n  Waiting for battles to settle...")
        time.sleep(1.0)  # Let animations finish
        
        # Single check at bottom
        print("  Checking for rewards at bottom...")
        battle_pos = self.finder.find_battle_with_rewards()
        
        if battle_pos:
            print(f"  ✓ REWARDS FOUND at bottom!")
            return battle_pos
        else:
            print(f"  ✗ No rewards found")
            return None

    # ==================== MAIN RUN ====================
    
    def run(self, max_expansions=None):
        """
        Search through expansions for rewards
        max_expansions: override default (useful for B-series with fewer)
        """
        if max_expansions is None:
            max_expansions = self.max_expansions
        
        print("=" * 60)
        print(f"TEST 04: Expansion Search (up to {max_expansions} expansions)")
        print("=" * 60)
        input("\nPress ENTER to start scanning...")
        
        # Load battle list region
        if 'battle_list_region' in self.config:
            self.finder.battle_list_region = tuple(self.config['battle_list_region'])
            print(f"✓ Loaded battle list region")
        else:
            print("⚠️  No battle list region found")
            return
        
        # Initial check on current screen
        print("\n--- Quick check: Current screen ---")
        battle_pos = self.finder.find_battle_with_rewards()
        if battle_pos:
            print("✓ Found rewards immediately!")
            self.finder.show_detection_visually(battle_pos)
            return
        
        print("\n--- Starting Expansion Loop ---")
        total_checked = 0
        
        for expansion_num in range(1, max_expansions + 1):
            if expansion_num in self.checked_expansions:
                continue
            
            scrolls_needed = self.get_scrolls_for_expansion(expansion_num)
            slot_idx = self.get_visible_slot_index(expansion_num)
            
            print(f"\n===== Expansion #{expansion_num} =====")
            print(f"Scrolls needed: {scrolls_needed}")
            print(f"Slot to click: {slot_idx + 1}")
            
            # Open expansions menu (resets to top)
            self.click_expansions_button()
            
            # Scroll to position if needed
            if scrolls_needed > 0:
                self.perform_scroll_gesture(scrolls_needed)
            
            # Open expansion
            opened = self.open_visible_expansion(slot_idx)
            if not opened:
                print("✗ Could not open expansion")
                break
            
            # Scan inside
            total_checked += 1
            battle_pos = self.scan_expansion_for_rewards()
            
            if battle_pos:
                print(f"\n✓ Found rewards in Expansion #{expansion_num}!")
                self.finder.show_detection_visually(battle_pos)
                return
            
            print(f"✗ No rewards in Expansion #{expansion_num}")
            self.checked_expansions.add(expansion_num)
            time.sleep(1)
        
        print(f"\n✗ No rewards found after scanning {max_expansions} expansion(s)")
        print(f"Total expansions checked: {total_checked}")


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 04: EXPANSION SEARCH")
    print("="*60)
    
    print("\nSetup:")
    print("  1. Navigate to Solo Battle → Intermediate difficulty")
    print("  2. Make sure you're on a screen where you can access Expansions")
    
    input("\nPress ENTER when ready...")
    
    searcher = ExpansionSearcherADB()
    searcher.run()


if __name__ == "__main__":
    main()