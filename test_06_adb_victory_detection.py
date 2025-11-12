#!/usr/bin/env python3
"""
TEST 06: Battle End Detection (ADB Version)
Simple and reliable: Detect FULL SCREEN white flash (single check)
"""

import cv2
import numpy as np
import time
from adb_controller import ADBController


class BattleEndDetectorADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)
        print("✓ Battle End Detector initialized (full screen white flash detection)")
    
    def detect_full_screen_white(self, threshold=200, white_percentage=0.90):
        """
        Detect if ENTIRE screen is white
        
        Args:
            threshold: Brightness value to count as "white" (0-255, default 200)
            white_percentage: What % of screen must be white (default 90%)
        
        Returns True if full screen white detected
        """
        # Take FULL screenshot via ADB
        screenshot = self.controller.screenshot_cv()
        
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Count pixels above threshold (white pixels)
        white_pixels = np.sum(gray >= threshold)
        total_pixels = gray.size
        
        white_percent = white_pixels / total_pixels
        
        # Debug output
        print(f"[WHITE] {white_percent*100:.1f}% white (need {white_percentage*100:.0f}%)", end="\r")
        
        return white_percent >= white_percentage
    
    def monitor_battle_end(self, wait_before_start=30):
        """
        Monitor for battle end using full screen white detection
        Single check - no verification needed (no false positives during battle)
        wait_before_start: Seconds to wait before starting monitoring
        """
        print(f"\nWaiting {wait_before_start} seconds before monitoring starts...")
        for i in range(wait_before_start, 0, -1):
            print(f"Starting in {i}s...", end="\r")
            time.sleep(1)
        
        print("\n--- Monitoring for Battle End (Full Screen White) ---")
        print("Detection: ENTIRE screen turns white → Battle ended")
        print("Single check (no false positives during battle)\n")
        
        check_count = 0
        while True:
            try:
                check_count += 1
                
                # Check for full screen white - if detected, battle is over!
                if self.detect_full_screen_white(threshold=200, white_percentage=0.90):
                    print(f"\n✓✓✓ FULL SCREEN WHITE DETECTED (check #{check_count})")
                    print("✓✓✓ BATTLE END CONFIRMED!")
                    return True
                
                # Print periodic status (every 10 seconds)
                if check_count % 20 == 0:
                    print(f"\n[Check #{check_count}] Still monitoring...")
                
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopped by user")
                return False


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 06: BATTLE END DETECTION")
    print("="*60)
    
    print("\nSimple Full Screen White Detection:")
    print("  - Detects when ENTIRE screen turns white")
    print("  - Single check (instant detection)")
    print("  - Works for both victory and defeat")
    
    print("\nSetup:")
    print("  1. Start a battle in the emulator")
    print("  2. Let it run (AUTO should be on)")
    print("  3. This script will detect when battle ends")
    
    input("\nPress ENTER to start monitoring...")
    
    detector = BattleEndDetectorADB()
    detector.monitor_battle_end(wait_before_start=30)


if __name__ == "__main__":
    main()