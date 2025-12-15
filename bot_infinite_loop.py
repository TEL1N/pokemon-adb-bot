#!/usr/bin/env python3
"""
INFINITE BATTLE LOOP BOT (Multi-Instance Ready)
"""

import time
import argparse
import sys

# Import your workflow classes
# NOTE: You must update these classes to accept device_id in __init__
from test_05_adb_full_workflow import RewardBattleBotADB
from test_06_adb_victory_detection import BattleEndDetectorADB
from test_07_adb_universal_reset import UniversalResetADB

def run_infinite_battle_loop(device_id):
    print(f"\n[{device_id}] STARTING BOT INSTANCE...")
    
    # Initialize components with specific device ID
    try:
        # Pass device_id to your classes so they control the correct emulator
        battle_bot = RewardBattleBotADB(device_id)
        battle_end_detector = BattleEndDetectorADB(device_id)
        universal_reset = UniversalResetADB(device_id)
        
        print(f"[{device_id}]   ✓ All components initialized")
        print(f"[{device_id}]   ⏱️  Starting in 3 seconds...")
        time.sleep(3)
        
        cycle = 1
        battles_completed = 0
        resume_mode = False
        
        print(f"\n[{device_id}]   ==================================================")
        print(f"[{device_id}]   🎮 BOT IS NOW RUNNING")
        print(f"[{device_id}]   ==================================================")
        
        while True:
            print(f"\n[{device_id}]   ==================================================")
            print(f"[{device_id}]     CYCLE #{cycle} - Battles Won: {battles_completed}")
            print(f"[{device_id}]   ==================================================")
            
            try:
                # STAGE 1: FIND BATTLE
                if resume_mode:
                    print(f"[{device_id}]   [Stage 1/3] 🔄 RESUMING...")
                else:
                    print(f"[{device_id}]   [Stage 1/3] 🔍 Searching for battles with rewards...")
                
                battle_bot.run(resume_from_battle=resume_mode)
                
            except Exception as e:
                print(f"[{device_id}]   ❌ Search Error: {e}")
                time.sleep(5)
                resume_mode = False
                continue
            
            try:
                # STAGE 2: DETECT END
                print(f"[{device_id}]   [Stage 2/3] ⏳ Waiting for Battle End...")
                battle_end_detector.monitor_battle_end(wait_before_start=30)
                battles_completed += 1
                
            except Exception as e:
                print(f"[{device_id}]   ❌ Detection Error: {e}")
                time.sleep(5)
                resume_mode = False
                continue
            
            try:
                # STAGE 3: RESET
                print(f"[{device_id}]   [Stage 3/3] 🔄 Resetting...")
                universal_reset.run_universal_reset()
                
                # Sync state
                if battle_bot.is_beginner_exhausted():
                    battle_bot.current_difficulty = "intermediate"
                else:
                    battle_bot.reset_to_beginner()
                
                resume_mode = True
                
            except Exception as e:
                print(f"[{device_id}]   ❌ Reset Error: {e}")
                time.sleep(5)
                resume_mode = False
                continue
            
            cycle += 1
            time.sleep(3)

    except KeyboardInterrupt:
        print(f"\n[{device_id}] 🛑 STOPPED")

if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, required=True, help="ADB Device ID")
    args = parser.parse_args()
    
    run_infinite_battle_loop(args.device)