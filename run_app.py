import threading
import time
import os
from api.server import start_server
from api.controllers import orchestrator # <--- CRITICAL: Use the SHARED one

def run_dashboard():
    # Start the session on the SHARED orchestrator
    orchestrator.start_session()
    
    try:
        while True:
            # 1. Get stats from the SHARED instance
            stats = orchestrator.get_realtime_status()
            
            # 2. Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 3. Print the Output
            print("=== MONITORING ACTIVE (ADMIN MODE) ===")
            print(f"duration         : {stats.get('duration', 0):.2f}")
            print(f"keyboard_events  : {stats.get('keyboard_events', 0)}")
            print(f"mouse_moves      : {stats.get('mouse_moves', 0)}")
            print(f"mouse_clicks     : {stats.get('mouse_clicks', 0)}")
            print(f"app_switches     : {stats.get('app_switches', 0)}")
            print(f"stability        : {stats.get('stability', 0)}")
            print("======================================")
            print("Interact with ANY window to see changes.")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        orchestrator.end_session()

if __name__ == "__main__":
    # Start Flask in background
    threading.Thread(target=start_server, daemon=True).start()
    
    # Run Dashboard in main thread
    run_dashboard()