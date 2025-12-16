#!/usr/bin/env python3
"""
INFINITE BATTLE LOOP BOT (Multi-Instance Ready)
Each instance runs independently with its own progress tracking
"""

import time
import argparse
import sys

# Import your workflow classes
from test_05_adb_full_workflow import RewardBattleBotADB
from test_06_adb_victory_detection import BattleEndDetectorADB
from test_07_adb_universal_reset import UniversalResetADB


def run_infinite_battle_loop(device_id):
    """
    Run infinite battle loop for a specific device
    
    Args:
        device_id: ADB device identifier (e.g., 127.0.0.1:16416)
    """
    print(f"\n{'='*60}")
    print(f"[{device_id}] STARTING BOT INSTANCE")
    print(f"{'='*60}")
    
    # Initialize components with specific device ID
    try:
        print(f"[{device_id}] Initializing components...")
        
        # Each component gets the device_id
        battle_bot = RewardBattleBotADB(device_id)
        battle_end_detector = BattleEndDetectorADB(device_id)
        universal_reset = UniversalResetADB(device_id)
        
        print(f"[{device_id}] ✓ All components initialized")
        print(f"[{device_id}] ⏱️  Starting in 3 seconds...")
        time.sleep(3)
        
    except Exception as e:
        print(f"[{device_id}] ❌ Failed to initialize: {e}")
        return
    
    cycle = 1
    battles_completed = 0
    resume_mode = False
    
    print(f"\n[{device_id}] {'='*50}")
    print(f"[{device_id}] 🎮 BOT IS NOW RUNNING")
    print(f"[{device_id}] {'='*50}")
    
    while True:
        print(f"\n[{device_id}] {'='*50}")
        print(f"[{device_id}] CYCLE #{cycle} - Battles Won: {battles_completed}")
        print(f"[{device_id}] {'='*50}")
        
        try:
            # STAGE 1: FIND BATTLE
            if resume_mode:
                print(f"[{device_id}] [Stage 1/3] 🔄 RESUMING from last location...")
            else:
                print(f"[{device_id}] [Stage 1/3] 🔍 Searching for battles with rewards...")
            
            battle_bot.run(resume_from_battle=resume_mode)
            
        except Exception as e:
            print(f"[{device_id}] ❌ Search Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
            resume_mode = False
            continue
        
        try:
            # STAGE 2: DETECT BATTLE END
            print(f"[{device_id}] [Stage 2/3] ⏳ Waiting for Battle End...")
            battle_end_detector.monitor_battle_end(wait_before_start=30)
            battles_completed += 1
            print(f"[{device_id}] ✓ Battle #{battles_completed} completed!")
            
        except Exception as e:
            print(f"[{device_id}] ❌ Detection Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
            resume_mode = False
            continue
        
        try:
            # STAGE 3: RESET TO MENU
            print(f"[{device_id}] [Stage 3/3] 🔄 Resetting to menu...")
            universal_reset.run_universal_reset()
            
            # Sync bot state after reset
            # After universal reset, game is at Beginner difficulty
            if battle_bot.is_beginner_exhausted():
                battle_bot.current_difficulty = "intermediate"
            else:
                battle_bot.reset_to_beginner()
            
            resume_mode = True
            
        except Exception as e:
            print(f"[{device_id}] ❌ Reset Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
            resume_mode = False
            continue
        
        cycle += 1
        print(f"[{device_id}] Waiting 3 seconds before next cycle...")
        time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pokemon TCG Bot - Single Instance")
    parser.add_argument("--device", type=str, required=True, 
                        help="ADB Device ID (e.g., 127.0.0.1:16416)")
    args = parser.parse_args()
    
    try:
        run_infinite_battle_loop(args.device)
    except KeyboardInterrupt:
        print(f"\n[{args.device}] 🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n[{args.device}] ❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()