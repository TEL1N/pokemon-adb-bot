#!/usr/bin/env python3
"""
Progress Tracker - Remembers which expansions have been checked
Prevents re-checking exhausted expansions
"""

import json
from pathlib import Path


PROGRESS_FILE = "expansion_progress.json"


class ProgressTracker:
    def __init__(self):
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load progress from file"""
        path = Path(PROGRESS_FILE)
        
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
                print(f"Loaded progress: {PROGRESS_FILE}")
                return data
        else:
            # Initialize empty progress
            print("No progress file found, starting fresh")
            return {
                "intermediate_A": 0,
                "intermediate_B": 0,
                "advanced_A": 0,
                "advanced_B": 0,
                "expert_A": 0,
                "expert_B": 0
            }
    
    def save_progress(self):
        """Save progress to file"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)
        print(f"Progress saved to {PROGRESS_FILE}")
    
    def get_key(self, difficulty, series):
        """Get progress key for difficulty + series"""
        return f"{difficulty}_{series}"
    
    def get_start_position(self, difficulty, series):
        """
        Get which expansion to start from (1-indexed)
        Returns expansion number to start checking
        """
        key = self.get_key(difficulty, series)
        checked_count = self.progress.get(key, 0)
        
        # Start from next unchecked expansion
        return checked_count + 1
    
    def mark_checked(self, difficulty, series, expansion_num):
        """
        Mark an expansion as checked/exhausted
        Only updates if this is the next sequential expansion
        """
        key = self.get_key(difficulty, series)
        current = self.progress.get(key, 0)
        
        # Only update if checking sequentially
        if expansion_num == current + 1:
            self.progress[key] = expansion_num
            self.save_progress()
            print(f"  Marked {key} expansion #{expansion_num} as checked")
        elif expansion_num <= current:
            print(f"  (Already marked: {key} expansion #{expansion_num})")
        else:
            print(f"  Warning: Skipped expansion? Expected {current + 1}, got {expansion_num}")
    
    def is_series_exhausted(self, difficulty, series, total_expansions):
        """Check if all expansions in a series have been checked"""
        key = self.get_key(difficulty, series)
        checked = self.progress.get(key, 0)
        
        return checked >= total_expansions
    
    def is_difficulty_exhausted(self, difficulty, expansion_counts):
        """
        Check if all series in a difficulty are exhausted
        
        Args:
            difficulty: intermediate, advanced, or expert
            expansion_counts: dict like A: 11, B: 1
        """
        for series, count in expansion_counts.items():
            if not self.is_series_exhausted(difficulty, series, count):
                return False
        
        return True
    
    def is_fully_exhausted(self):
        """Check if everything is exhausted"""
        # Hardcoded expansion counts (update when new expansions release)
        expansion_counts = {"A": 11, "B": 1}
        
        difficulties = ["intermediate", "advanced", "expert"]
        
        for difficulty in difficulties:
            if not self.is_difficulty_exhausted(difficulty, expansion_counts):
                return False
        
        return True
    
    def reset_progress(self):
        """Clear all progress (start fresh)"""
        self.progress = {
            "intermediate_A": 0,
            "intermediate_B": 0,
            "advanced_A": 0,
            "advanced_B": 0,
            "expert_A": 0,
            "expert_B": 0
        }
        self.save_progress()
        print("Progress reset!")
    
    def get_summary(self):
        """Get human-readable summary"""
        lines = []
        lines.append("Progress Summary:")
        
        for difficulty in ["intermediate", "advanced", "expert"]:
            lines.append(f"\n{difficulty.upper()}:")
            for series in ["A", "B"]:
                key = self.get_key(difficulty, series)
                checked = self.progress.get(key, 0)
                lines.append(f"  {series}-series: {checked} expansion(s) checked")
        
        return "\n".join(lines)


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    print("="*60)
    print("PROGRESS TRACKER TEST")
    print("="*60)
    
    tracker = ProgressTracker()
    
    print("\n" + tracker.get_summary())
    
    print("\n--- Testing Functions ---")
    
    # Test: Where to start?
    start = tracker.get_start_position("intermediate", "A")
    print(f"\nShould start at Intermediate A expansion #{start}")
    
    # Test: Mark as checked
    print("\nMarking Intermediate A expansion #1 as checked...")
    tracker.mark_checked("intermediate", "A", 1)
    
    print("\n" + tracker.get_summary())
    
    # Test: Is exhausted?
    exhausted = tracker.is_series_exhausted("intermediate", "A", 11)
    print(f"\nIs Intermediate A exhausted? {exhausted}")
    
    print("\nTest complete!")