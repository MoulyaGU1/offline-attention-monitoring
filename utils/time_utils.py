import time
import os
from datetime import datetime

# Assuming all your classes are in their respective files/folders
from core.session_orchestrator import SessionOrchestrator
from utils.logger import Logger

def run_realtime_monitor():
    # 1. Initialize the Orchestrator
    orchestrator = SessionOrchestrator()
    logger = Logger.get_logger()
    
    print("--- Initializing Trackers ---")
    status = orchestrator.start_session()
    
    if status.get("status") == "session_started":
        print("Monitoring Started. Move your mouse or type to see updates.")
        time.sleep(1) # Give threads a moment to spin up
    else:
        print("Failed to start session.")
        return

    try:
        while True:
            # 2. Fetch the real-time status we added to Orchestrator
            stats = orchestrator.get_realtime_status()
            
            # 3. Clear the console for a clean dashboard look
            # Windows: 'cls', Linux/macOS: 'clear'
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 4. Print the formatted output exactly as you requested
            print(f"{'METRIC':<18} : {'VALUE'}")
            print("-" * 35)
            print(f"app_switches     : {stats.get('app_switches', 0)}")
            print(f"duration         : {stats.get('duration', 0):.6f}")
            print(f"fragmentation    : {stats.get('fragmentation', 0)}")
            print(f"idle_time        : {stats.get('idle_time', 0)}")
            print(f"keyboard_events  : {stats.get('keyboard_events', 0)}")
            print(f"mouse_clicks     : {stats.get('mouse_clicks', 0)}")
            print(f"mouse_moves      : {stats.get('mouse_moves', 0)}")
            print(f"patterns         : {stats.get('patterns', {})}")
            print(f"stability        : {stats.get('stability', 0)}")
            print(f"timeline         : {stats.get('timeline', {})}")
            print("-" * 35)
            print("Press Ctrl+C to end session and generate final report.")
            
            time.sleep(0.5) # Refresh rate

    except KeyboardInterrupt:
        print("\nStopping session...")
        final_report = orchestrator.end_session()
        print("--- FINAL SESSION REPORT ---")
        print(final_report)

if __name__ == "__main__":
    run_realtime_monitor()