import sqlite3
from datetime import datetime

class Session:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.events = []
        # Path must match your routes.py
        self.db_path = r"C:\Users\lenovo\OneDrive\Documents\Desktop\Moulya\attention-mapping-tool\attention_history.db"

    def start(self):
        self.start_time = datetime.now()
        print(f"[*] Session started at {self.start_time}")

    def add_event(self, event):
        self.events.append(event)

    def end(self):
        self.end_time = datetime.now()
        
        # 1. Calculate Duration
        duration = (self.end_time - self.start_time).total_seconds()
        
        # 2. Extract Metrics from Events (Example Logic)
        # You can expand this to count specific app names from self.events
        top_app = "General Context"
        if self.events:
            # Simple logic: assume the last event's app is the top app
            # Or iterate through events to find the most frequent one
            top_app = self.events[-1].get('app_name', 'General Context')

        # 3. SAVE TO DATABASE
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO session_history 
                (start_time, duration, top_app, app_jumps, idle_duration)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                round(duration, 2), 
                top_app, 
                len(set(e.get('app_name') for e in self.events if 'app_name' in e)), # Unique apps
                0.0 # Placeholder for idle logic
            ))
            
            # 4. GET THE NEW ID (Required for your Heatmap feature)
            new_session_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            print(f"[+] Session {new_session_id} saved successfully.")
            return new_session_id
            
        except Exception as e:
            print(f"[-] Database Error: {e}")
            return None

    def get_duration(self):
        if not self.end_time and self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds()