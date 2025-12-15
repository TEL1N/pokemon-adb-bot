#!/usr/bin/env python3
"""
Progress Tracker - Multi-Instance Supported & Fixed
"""

import json
from pathlib import Path


class ProgressTracker:
    def __init__(self, device_id=None):
        # Create a unique filename for this device
        if device_id:
            # Sanitize device ID (replace : with _)
            sanitized_id = device_id.replace(":", "_").replace(".", "_")
            self.filename = f"expansion_progress_{sanitized_id}.json"
        else:
            self.filename = "expansion_progress.json"
            
        print(f"[{device_id or 'Default'}] Using progress file: {self.filename}")
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load progress from file"""
        path = Path(self.filename)
        
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data
            except:
                print(f"Error loading {self.filename}, starting fresh")
        
        # Initialize empty progress
        return {
            "beginner_A": 0, "beginner_B": 0,
            "intermediate_A": 0, "intermediate_B": 0,
            "advanced_A": 0, "advanced_B": 0,
            "expert_A": 0, "expert_B": 0
        }
    
    def save_progress(self):
        """Save progress to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_key(self, difficulty, series):
        return f"{difficulty}_{series}"
    
    def get_start_position(self, difficulty, series):
        key = self.get_key(difficulty, series)
        checked_count = self.progress.get(key, 0)
        return checked_count + 1
    
    def mark_checked(self, difficulty, series, expansion_num):
        key = self.get_key(difficulty, series)
        current = self.progress.get(key, 0)
        
        # Logic: Always save the highest number we've reached
        if expansion_num >= current + 1:
            self.progress[key] = expansion_num
            self.save_progress()
    
    def is_series_exhausted(self, difficulty, series, total_expansions):
        """Check if a specific series is fully checked"""
        key = self.get_key(difficulty, series)
        checked = self.progress.get(key, 0)
        return checked >= total_expansions

    def is_difficulty_exhausted(self, difficulty, expansion_counts):
        """
        Check if all series in a difficulty are exhausted
        Args:
            difficulty: intermediate, advanced, etc.
            expansion_counts: dict like {'A': 11, 'B': 1}
        """
        for series, count in expansion_counts.items():
            if not self.is_series_exhausted(difficulty, series, count):
                return False
        return True
    
    def is_fully_exhausted(self):
        """Check if EVERYTHING is exhausted"""
        # Hardcoded expansion counts (A=11, B=1 for now)
        expansion_counts = {"A": 11, "B": 1}
        difficulties = ["beginner", "intermediate", "advanced", "expert"]
        
        for difficulty in difficulties:
            if not self.is_difficulty_exhausted(difficulty, expansion_counts):
                return False
        
        return True
        
    def reset_progress(self):
        self.progress = {k: 0 for k in self.progress}
        self.save_progress()