#!/usr/bin/env python3
"""
Progress Tracker - IN-MEMORY ONLY for Parallelization
Each bot instance gets its own tracker that resets when bot closes
No file saving - ports can change between sessions
"""


class ProgressTracker:
    def __init__(self, device_id=None):
        """
        Initialize progress tracker (in-memory only)
        
        Args:
            device_id: For logging purposes only, not used for file naming
        """
        self.device_id = device_id or "unknown"
        print(f"[{self.device_id}] Progress tracker initialized (in-memory, resets on close)")
        
        # In-memory progress - starts fresh every time
        self.progress = {
            "beginner_A": 0, "beginner_B": 0,
            "intermediate_A": 0, "intermediate_B": 0,
            "advanced_A": 0, "advanced_B": 0,
            "expert_A": 0, "expert_B": 0
        }
    
    def get_key(self, difficulty, series):
        return f"{difficulty}_{series}"
    
    def get_start_position(self, difficulty, series):
        """Get which expansion to start from (1-indexed)"""
        key = self.get_key(difficulty, series)
        checked_count = self.progress.get(key, 0)
        return checked_count + 1
    
    def mark_checked(self, difficulty, series, expansion_num):
        """Mark an expansion as checked (no rewards found)"""
        key = self.get_key(difficulty, series)
        current = self.progress.get(key, 0)
        
        # Save the highest number we've reached
        if expansion_num >= current + 1:
            self.progress[key] = expansion_num
            print(f"  [{self.device_id}] Marked {key} expansion #{expansion_num} as checked")
    
    def is_series_exhausted(self, difficulty, series, total_expansions):
        """Check if a specific series is fully checked"""
        key = self.get_key(difficulty, series)
        checked = self.progress.get(key, 0)
        return checked >= total_expansions

    def is_difficulty_exhausted(self, difficulty, expansion_counts):
        """
        Check if all series in a difficulty are exhausted
        Args:
            difficulty: beginner, intermediate, advanced, expert
            expansion_counts: dict like {'A': 11, 'B': 1}
        """
        for series, count in expansion_counts.items():
            if not self.is_series_exhausted(difficulty, series, count):
                return False
        return True
    
    def is_fully_exhausted(self):
        """Check if ALL difficulties and series are exhausted"""
        expansion_counts = {"A": 11, "B": 1}
        difficulties = ["beginner", "intermediate", "advanced", "expert"]
        
        for difficulty in difficulties:
            if not self.is_difficulty_exhausted(difficulty, expansion_counts):
                return False
        
        return True
        
    def reset_progress(self):
        """Reset all progress to zero"""
        self.progress = {k: 0 for k in self.progress}
        print(f"  [{self.device_id}] Progress reset to zero")
    
    def get_status(self):
        """Get current progress status for logging"""
        return dict(self.progress)