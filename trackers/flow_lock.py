import time
import json
import os
import threading  # Added for thread-safe notifications
import pygetwindow as gw
from win10toast import ToastNotifier
import winsound 

toaster = ToastNotifier()

def load_blacklist():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'blacklist.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"distractions": ["YouTube", "Facebook", "Instagram"]}

def start_flow_lock(committed_app, duration_mins):
    blacklist_data = load_blacklist()
    distractions = blacklist_data.get('distractions', [])
    
    end_time = time.time() + (int(duration_mins) * 60)
    print(f"🔒 Flow Lock Engaged: {committed_app} for {duration_mins}m")

    while time.time() < end_time:
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                current_title = active_window.title.lower()
                target = committed_app.lower()
                
                is_distracted = any(d.lower() in current_title for d in distractions)
                is_off_task = target not in current_title

                if is_distracted and is_off_task:
                    # 1. Play System Sound (Safe on main thread)
                    winsound.Beep(1000, 1000) 
                    
                    # 2. Fire notification in a separate thread to avoid WNDPROC/LRESULT errors
                    def notify():
                        try:
                            toaster.show_toast(
                                "⚠️ Attention Leak",
                                f"Focus remained on {committed_app}. Return to flow?",
                                duration=5,
                                threaded=True
                            )
                        except:
                            pass

                    threading.Thread(target=notify, daemon=True).start()
                    
                    time.sleep(20) # Prevent notification spam
            
            time.sleep(2)
        except Exception:
            # If a window gives a 'NoneType' error during switch, just ignore and wait
            time.sleep(1)