#!/usr/bin/env python3
"""
TEST 06: Victory Detection (ADB Version)
Monitors for victory screen using template matching
"""

import cv2
import numpy as np
import time
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from adb_controller import ADBController


TEMPLATE_PATH = "pokemon_tcg_screenshots/victory_screen.png"


class VictoryDetectorADB:
    def __init__(self, device_id=None):
        self.controller = ADBController(device_id)
        
        # Load template
        self.template_color = cv2.imread(TEMPLATE_PATH)
        if self.template_color is None:
            raise FileNotFoundError(f"Missing template: {TEMPLATE_PATH}")
        print(f"✓ Loaded template {TEMPLATE_PATH}, shape={self.template_color.shape}")
        
        # Prepare grayscale cropped template
        self.template_gray = cv2.cvtColor(self.template_color, cv2.COLOR_BGR2GRAY)
        self.template_crop = self._crop_focus_area(self.template_gray)
    
    def _crop_focus_area(self, img):
        """Crop top 25% height and middle 60% width"""
        h, w = img.shape
        top, bottom = 0, int(h * 0.25)
        left, right = int(w * 0.20), int(w * 0.80)
        return img[top:bottom, left:right]
    
    def grab_gray_frame(self):
        """Take screenshot via ADB and process it"""
        # Take full screenshot
        frame = self.controller.screenshot_cv()
        
        # Convert to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Crop focus area
        return self._crop_focus_area(frame_gray)
    
    def detect_victory(self, threshold=0.40):
        """
        Check if victory screen is showing
        Returns True if detected, False otherwise
        """
        frame_crop = self.grab_gray_frame()
        if frame_crop is None:
            return False
        
        # Resize template to match frame
        template_resized = cv2.resize(self.template_crop, (frame_crop.shape[1], frame_crop.shape[0]))
        
        # Equalize brightness
        frame_eq = cv2.equalizeHist(frame_crop)
        template_eq = cv2.equalizeHist(template_resized)
        
        # Compute SSIM
        score, _ = ssim(frame_eq, template_eq, full=True)
        
        # Compute edge similarity
        edges_frame = cv2.Canny(frame_eq, 50, 150)
        edges_template = cv2.Canny(template_eq, 50, 150)
        score_edges, _ = ssim(edges_frame, edges_template, full=True)
        
        # Combined average
        final_score = (score + score_edges) / 2.0
        print(f"[DEBUG] SSIM: {score:.3f}  Edge: {score_edges:.3f}  Avg: {final_score:.3f}", end="\r")
        
        return final_score >= threshold
    
    def monitor_victory_screen(self, wait_before_start=30):
        """
        Monitor for victory screen
        wait_before_start: Seconds to wait before starting monitoring
        """
        print(f"\nWaiting {wait_before_start} seconds before monitoring starts...")
        for i in range(wait_before_start, 0, -1):
            print(f"Starting in {i}s...", end="\r")
            time.sleep(1)
        
        print("\n--- Monitoring for Victory screen ---")
        
        while True:
            try:
                if self.detect_victory():
                    print("\n✓ Victory detected!")
                    return True
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopped by user")
                return False


def main():
    print("="*60)
    print("POKEMON TCG ADB - TEST 06: VICTORY DETECTION")
    print("="*60)
    
    print("\nSetup:")
    print("  1. Start a battle in the emulator")
    print("  2. Let it run (AUTO should be on)")
    print("  3. This script will detect when you win")
    
    input("\nPress ENTER to start monitoring...")
    
    detector = VictoryDetectorADB()
    detector.monitor_victory_screen(wait_before_start=30)


if __name__ == "__main__":
    main()