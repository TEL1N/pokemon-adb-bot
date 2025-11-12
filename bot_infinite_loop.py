#!/usr/bin/env python3
"""
INFINITE BATTLE LOOP BOT (ADB Version)
Runs forever combining all workflows:
1. Find and start battle (test_05)
2. Detect battle end (test_06 - white flash)
3. Reset to base state (test_07)
4. Repeat FOREVER
"""

import time
from test_05_adb_full_workflow import RewardBattleBotADB
from test_06_adb_victory_detection import BattleEndDetectorADB
from test_07_adb_universal_reset import UniversalResetADB


def run_infinite_battle_loop():
    print("\n" + "="*70)
    print(" "*15 + "POKEMON TCG INFINITE BATTLE BOT")
    print("="*70)
    print("\n🤖 Bot Features:")
    print("  ✓ Runs inside emulator (your PC stays free!)")
    print("  ✓ Finds battles with rewards automatically")
    print("  ✓ Searches all difficulties (Intermediate → Advanced → Expert)")
    print("  ✓ Searches all series (A + B)")
    print("  ✓ Tracks progress (never rechecks exhausted expansions)")
    print("  ✓ Starts battles with AUTO enabled")
    print("  ✓ Detects battle end (white flash detection)")
    print("  ✓ Resets to Intermediate after each battle")
    print("  ✓ Resumes same expansion to find more battles")
    print("  ✓ Runs FOREVER until you press CTRL+C")
    print("\n⚠️  IMPORTANT:")
    print("  - Make sure Pokemon TCG Pocket is open")
    print("  - Bot will run continuously")
    print("  - Press CTRL+C to stop at any time")
    print("\n" + "="*70)
    
    input("\n✅ Press ENTER to start the infinite loop...")
    
    print("\n🚀 Initializing bot components...")
    
    # Initialize all components
    battle_bot = RewardBattleBotADB()
    battle_end_detector = BattleEndDetectorADB()
    universal_reset = UniversalResetADB()
    
    print("✓ All components initialized")
    print("\n⏱️  Starting in 3 seconds...")
    time.sleep(3)
    
    cycle = 1
    battles_completed = 0
    
    # First run is a fresh search
    resume_mode = False
    
    print("\n" + "="*70)
    print("🎮 BOT IS NOW RUNNING")
    print("="*70)
    
    while True:
        print(f"\n{'='*70}")
        print(f"  CYCLE #{cycle} - Total Battles Completed: {battles_completed}")
        print(f"{'='*70}")
        
        try:
            # ==================== STAGE 1: FIND & START BATTLE ====================
            if resume_mode:
                print("\n[Stage 1/3] 🔄 RESUMING from last battle location...")
            else:
                print("\n[Stage 1/3] 🔍 Searching for battles with rewards...")
            
            battle_bot.run(resume_from_battle=resume_mode)
            print("✓ Battle started successfully")
            
        except Exception as e:
            print(f"\n❌ [ERROR] Battle search failed: {e}")
            print("⏳ Waiting 5 seconds before retry...")
            time.sleep(5)
            resume_mode = False  # Reset resume mode on error
            continue
        
        try:
            # ==================== STAGE 2: WAIT FOR BATTLE END ====================
            print("\n[Stage 2/3] ⏳ Monitoring for Battle End (white flash)...")
            print("  (Will wait 30 seconds before monitoring starts)")
            
            battle_end_detector.monitor_battle_end(wait_before_start=30)
            
            print("\n✓ Battle end detected!")
            battles_completed += 1
            print(f"🎉 Battles completed this session: {battles_completed}")
            
        except Exception as e:
            print(f"\n❌ [ERROR] Battle end detection failed: {e}")
            print("⏳ Waiting 5 seconds before retry...")
            time.sleep(5)
            resume_mode = False  # Reset resume mode on error
            continue
        
        try:
            # ==================== STAGE 3: RESET TO BASE STATE ====================
            print("\n[Stage 3/3] 🔄 Running Universal Reset Flow...")
            print("  (This takes ~90 seconds with safe delays)")
            
            universal_reset.run_universal_reset()
            print("✓ Reset complete")
            
            # CRITICAL: Reset bot's state after universal reset
            print("\n🔄 Syncing bot state with game state...")
            battle_bot.reset_to_intermediate()
            print("✓ Bot state synced (back to Intermediate)")
            
            # Enable resume mode for next cycle
            resume_mode = True
            print("✓ Next cycle will RESUME from last expansion")
            
        except Exception as e:
            print(f"\n❌ [ERROR] Universal reset failed: {e}")
            print("⏳ Waiting 5 seconds before retry...")
            time.sleep(5)
            resume_mode = False  # Reset resume mode on error
            continue
        
        # ==================== CYCLE COMPLETE ====================
        print(f"\n{'='*70}")
        print(f"  ✅ CYCLE #{cycle} COMPLETE")
        print(f"  📊 Session Stats: {battles_completed} battle(s) completed")
        print(f"{'='*70}")
        
        cycle += 1
        
        print("\n⏸️  Starting next cycle in 3 seconds...")
        time.sleep(3)


def main():
    try:
        run_infinite_battle_loop()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("  🛑 BOT STOPPED BY USER")
        print("="*70)
        print("\n👋 Thanks for using the Pokemon TCG Infinite Battle Bot!")
        print("💾 Progress has been saved automatically")


if __name__ == "__main__":
    main()