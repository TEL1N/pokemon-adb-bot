#!/usr/bin/env python3
"""
TEST 05: Full Workflow (ADB Version)
Complete battle bot with:
- Difficulty switching (Intermediate → Advanced → Expert)
- Series switching (A/B)
- Progress tracking
- AUTO/BATTLE clicking
"""

import json
import time
from adb_controller import ADBController
from test_03_adb_find_battles import BattleFinderADB
from test_04_adb_expansions import ExpansionSearcherADB
from progress_tracker import ProgressTracker


# Expansion counts per series
EXPANSION_COUNTS = {
    "A": 11,
    "B": 1  # Update when more B-series expansions release
}


class RewardBattleBotADB:
    # CHANGE THIS LINE:
    def __init__(self, device_id=None): 
        # Pass device_id to the controller and tracker
        self.adb = ADBController(device_id) 
        self.tracker = ProgressTracker(device_id) 
        self.device_id = device_id
        self.controller = ADBController(device_id)
        self.finder = BattleFinderADB(device_id)
        self.expansion_searcher = ExpansionSearcherADB(device_id)
        
        self.config = self.load_config()
        self.progress = ProgressTracker()
        
        # Track current game state
        self.current_series = "A"
        self.current_difficulty = "beginner"
        
        # Track last battle location for resuming
        self.last_battle_location = None  # (difficulty, series, expansion_num)
    
    def load_config(self):
        """Load calibrated coordinates"""
        try:
            with open('adb_config.json', 'r') as f:
                config = json.load(f)
                print("✓ Loaded calibration config")
                
                # DEBUG: Show series button coordinates
                if "series_buttons" in config:
                    print(f"  Series buttons loaded:")
                    print(f"    A-series: {config['series_buttons'].get('A')}")
                    print(f"    B-series: {config['series_buttons'].get('B')}")
                else:
                    print("  ⚠️ WARNING: No series_buttons in config!")
                
                return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return {}
    
    # ==================== NAVIGATION ====================
    
    def switch_to_difficulty(self, difficulty_name):
        """Switch to a different difficulty (CONDITIONAL SCROLLING)"""
        difficulty_buttons = self.config.get("difficulty_buttons", {})
        coords = tuple(difficulty_buttons.get(difficulty_name, (0, 0)))
        
        print(f"\n--- Switching to {difficulty_name.upper()} difficulty ---")
        
        # Step 1: Press BACK once to return to Solo Battles screen
        print("  [Step 1/3] Pressing BACK to return to Solo Battles...")
        self.controller.press_back(delay=2)
        
        # Step 2: CONDITIONAL SCROLL - Only scroll if NOT switching to Beginner
        if difficulty_name != "beginner":
            print("  [Step 2/3] Scrolling to reveal difficulties...")
            scroll_config = self.config.get("difficulty_scroll", {})
            start = tuple(scroll_config.get("start", (0, 0)))
            end = tuple(scroll_config.get("end", (0, 0)))
            
            for i in range(2):
                print(f"    Scroll {i+1}/2")
                self.controller.swipe_with_hold(*start, *end, duration=400, hold_time=1000, delay=1)
        else:
            print("  [Step 2/3] Skipping scroll (Beginner is already visible)")
        
        # Step 3: Click difficulty button
        print(f"  [Step 3/3] Clicking {difficulty_name.upper()} at {coords}...")
        self.controller.tap(*coords)
        time.sleep(2)
        
        self.current_difficulty = difficulty_name
        print(f"✓ Now on {difficulty_name.upper()} difficulty")
    
    def reset_to_beginner(self):
        """Reset state after universal reset (game defaults to Beginner)"""
        print("\n--- Resetting state after universal reset ---")
        self.current_difficulty = "beginner"
        self.current_series = "A"
        print("✓ Bot state reset: Beginner difficulty, A-series")
    
    def ensure_series(self, target_series):
        """Switch to A or B series if needed"""
        if self.current_series == target_series:
            print(f"  Already on {target_series}-series")
            return
        
        series_buttons = self.config.get("series_buttons", {})
        coords = tuple(series_buttons.get(target_series, (0, 0)))
        
        print(f"  Switching to {target_series}-series...")
        
        # CRITICAL: Must click expansions button FIRST to refresh the menu
        print(f"    Step 1: Opening expansions menu...")
        self.expansion_searcher.click_expansions_button()
        
        # THEN click the series button
        print(f"    Step 2: Clicking {target_series}-series button at {coords}...")
        self.controller.tap(*coords)
        time.sleep(1.5)
        
        self.current_series = target_series
        print(f"  ✓ Switched to {target_series}-series")
    
    # ==================== BATTLE ENGAGEMENT ====================
    
    def click_auto_and_battle(self):
        """Click AUTO then BATTLE buttons"""
        auto = tuple(self.config.get("auto_button", (0, 0)))
        battle = tuple(self.config.get("battle_button", (0, 0)))
        
        if auto == (0, 0) or battle == (0, 0):
            print("⚠️ AUTO/BATTLE buttons not calibrated")
            return
        
        print(f"Clicking AUTO at {auto}...")
        self.controller.tap(*auto)
        time.sleep(1.2)
        
        print(f"Clicking BATTLE at {battle}...")
        self.controller.tap(*battle)
        time.sleep(1.5)
    
    def engage_battle(self, battle_pos):
        """Click battle card and start it"""
        if not battle_pos:
            print("⚠️ No battle position provided")
            return
        
        click_x, click_y = battle_pos
        print(f"\nClicking battle at ({click_x}, {click_y})...")
        self.controller.tap(click_x, click_y)
        time.sleep(2)
        
        self.click_auto_and_battle()
        print("\n✓ Battle started!")
        print("✓ Progress saved!")
    
    # ==================== EXPANSION SCANNING ====================
    def is_beginner_exhausted(self):
        """Check if Beginner difficulty is fully exhausted"""
        return self.progress.is_difficulty_exhausted("beginner", EXPANSION_COUNTS)
    
    def scan_series_for_rewards(self, series_name, expansion_count):
        """
        Scan expansions in current series
        Returns battle position if found, else None
        """
        print(f"\n--- Scanning {series_name}-series ({expansion_count} expansions) ---")
        
        # Get where to start based on progress
        start_from = self.progress.get_start_position(self.current_difficulty, series_name)
        
        if start_from > expansion_count:
            print(f"  ✓ All {series_name}-series expansions already checked!")
            return None
        
        print(f"  Starting from expansion #{start_from}")
        
        for expansion_num in range(start_from, expansion_count + 1):
            scrolls = self.expansion_searcher.get_scrolls_for_expansion(expansion_num)
            slot_idx = self.expansion_searcher.get_visible_slot_index(expansion_num)
            
            print(f"\n  === {series_name}-series Expansion #{expansion_num} ===")
            
            # Step 1: Open expansions menu fresh (this resets the list to top)
            print(f"    [Step 1/3] Opening expansions menu...")
            self.expansion_searcher.click_expansions_button()
            
            # Step 2: CRITICAL - Click the series button to switch to correct series
            print(f"    [Step 2/3] Clicking {series_name}-series button...")
            series_buttons = self.config.get("series_buttons", {})
            series_coords = tuple(series_buttons.get(series_name, (0, 0)))
            
            if series_coords == (0, 0):
                print(f"    ✗ ERROR: {series_name}-series button not calibrated!")
                return None
            
            print(f"    Tapping {series_name}-series at {series_coords}...")
            self.controller.tap(*series_coords)
            time.sleep(2)  # Wait for series to switch and load
            
            # Step 3: Scroll to position if needed
            print(f"    [Step 3/3] Navigating to expansion #{expansion_num}...")
            if scrolls > 0:
                print(f"    Scrolling {scrolls} time(s)...")
                self.expansion_searcher.perform_scroll_gesture(scrolls)
            
            # Step 4: Open expansion
            print(f"    Opening expansion slot #{slot_idx + 1}...")
            opened = self.expansion_searcher.open_visible_expansion(slot_idx)
            if not opened:
                print("  ✗ Could not open expansion")
                self.progress.mark_checked(self.current_difficulty, series_name, expansion_num)
                continue
            
            # Step 5: Scan inside expansion
            print(f"    Scanning inside expansion for rewards...")
            battle_pos = self.expansion_searcher.scan_expansion_for_rewards()
            
            if battle_pos:
                print(f"\n✓✓✓ REWARDS FOUND in {series_name}-series Expansion #{expansion_num}!")
                # Save location but DON'T mark as exhausted
                self.last_battle_location = (self.current_difficulty, series_name, expansion_num)
                print(f"  📍 Saved location for resume: {self.last_battle_location}")
                return battle_pos
            
            # No rewards - mark as exhausted
            print(f"  ✗ No rewards in expansion #{expansion_num}")
            self.progress.mark_checked(self.current_difficulty, series_name, expansion_num)
            time.sleep(0.5)
        
        return None
    
    def check_difficulty_all_series(self):
        """
        Check both A and B series for current difficulty
        Returns battle position if found, else None
        """
        print(f"\n{'='*60}")
        print(f"CHECKING {self.current_difficulty.upper()} DIFFICULTY")
        print(f"{'='*60}")
        
        # Check if A-series exhausted
        a_exhausted = self.progress.is_series_exhausted(
            self.current_difficulty, "A", EXPANSION_COUNTS["A"]
        )
        
        # Check if B-series exhausted
        b_exhausted = self.progress.is_series_exhausted(
            self.current_difficulty, "B", EXPANSION_COUNTS["B"]
        )
        
        if a_exhausted and b_exhausted:
            print(f"✓ {self.current_difficulty.upper()} fully exhausted")
            return None
        
        # Check A-series
        if not a_exhausted:
            print(f"\n--- Checking A-series ---")
            self.current_series = "A"  # Update state
            battle_pos = self.scan_series_for_rewards("A", EXPANSION_COUNTS["A"])
            if battle_pos:
                return battle_pos
        else:
            print(f"\n✓ {self.current_difficulty.upper()} A-series already checked")
        
        # Check B-series
        if not b_exhausted:
            print(f"\n--- Checking B-series ---")
            self.current_series = "B"  # Update state
            battle_pos = self.scan_series_for_rewards("B", EXPANSION_COUNTS["B"])
            if battle_pos:
                return battle_pos
        else:
            print(f"\n✓ {self.current_difficulty.upper()} B-series already checked")
        
        # Exit expansions menu
        print(f"\n✗ No rewards in {self.current_difficulty.upper()}")
        
        
        return None
    
    # ==================== MAIN RUN ====================
    
    def run(self, resume_from_battle=False):
        """
        Main bot workflow
        resume_from_battle: If True, resumes from last battle location
        """
        print("=" * 60)
        print("FULL WORKFLOW BOT (ADB VERSION)")
        print("=" * 60)
        
        if resume_from_battle and self.last_battle_location:
            print(f"RESUMING from: {self.last_battle_location}")
        else:
            print("Will check: Beginner → Intermediate → Advanced → Expert")
            print("Each difficulty: A-series → B-series")
        
        print("\nStarting in 2 seconds...")
        time.sleep(2)
        
        # Load battle list region
        if 'battle_list_region' in self.config:
            self.finder.battle_list_region = tuple(self.config['battle_list_region'])
            self.expansion_searcher.finder.battle_list_region = tuple(self.config['battle_list_region'])
            print("✓ Loaded battle list region")
        else:
            print("⚠️ No battle list region found")
            return
        
        # Resume from battle if needed
        if resume_from_battle and self.last_battle_location:
            difficulty, series, expansion_num = self.last_battle_location
            print(f"\n--- RESUMING: {difficulty.upper()} {series}-series Expansion #{expansion_num} ---")
            
            # Sync state
            if self.current_difficulty != difficulty:
                self.switch_to_difficulty(difficulty)
            
            # Navigate to expansion and scan
            self.expansion_searcher.click_expansions_button()
            self.ensure_series(series)
            
            scrolls = self.expansion_searcher.get_scrolls_for_expansion(expansion_num)
            if scrolls > 0:
                self.expansion_searcher.perform_scroll_gesture(scrolls)
            
            slot_idx = self.expansion_searcher.get_visible_slot_index(expansion_num)
            opened = self.expansion_searcher.open_visible_expansion(slot_idx)
            
            if opened:
                battle_pos = self.expansion_searcher.scan_expansion_for_rewards()
                if battle_pos:
                    print(f"\n✓✓✓ FOUND another battle in same expansion!")
                    self.engage_battle(battle_pos)
                    return
                else:
                    print(f"✗ No more battles in this expansion")
                    self.progress.mark_checked(difficulty, series, expansion_num)
            
            self.last_battle_location = None
        
        # Check if fully exhausted
        if self.progress.is_fully_exhausted():
            print("\n" + "="*60)
            print("ALL EXPANSIONS ALREADY CHECKED!")
            print("="*60)
            return
        
        # Quick check on current screen
        print("\n--- Quick check: Current screen ---")
        battle_pos = self.finder.find_battle_with_rewards()
        if battle_pos:
            print("✓ Rewards found immediately!")
            self.engage_battle(battle_pos)
            return
        
        # Check all difficulties in order
        difficulties = ["beginner","intermediate", "advanced", "expert"]
        start_idx = difficulties.index(self.current_difficulty) if resume_from_battle else 0

        for i in range(start_idx, len(difficulties)):
            difficulty = difficulties[i]
            
            # Switch difficulty if not first one AND not current difficulty
            if difficulty != self.current_difficulty:
                self.switch_to_difficulty(difficulty)
            else:
                print(f"\n--- Already on {difficulty.upper()} difficulty ---")
            
            # Check all series for this difficulty
            battle_pos = self.check_difficulty_all_series()
            
            if battle_pos:
                print(f"\n✓✓✓ FOUND BATTLE in {difficulty.upper()}!")
                self.engage_battle(battle_pos)
                return
        
        # No rewards anywhere
        print("\n" + "="*60)
        print("NO REWARDS FOUND IN ANY DIFFICULTY")
        print("="*60)


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 05: FULL WORKFLOW")
    print("="*60)
    
    print("\nSetup:")
    print("  1. Make sure emulator is running")
    print("  2. Pokemon TCG Pocket is open")
    print("  3. You're at the main menu")
    
    input("\nPress ENTER to start...")
    
    bot = RewardBattleBotADB()
    bot.run()


if __name__ == "__main__":
    main()