import sqlite3
import os
import time
import threading
from datetime import datetime
import pygetwindow as gw
from pynput import mouse, keyboard

# --- DATABASE INITIALIZATION ---
def init_db():
    db_path = 'attention_history.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Stores Raw Interaction Timestamps
    cursor.execute('''CREATE TABLE IF NOT EXISTS interaction_signals 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
         signal_type TEXT)''') 

    # Consolidated Session History 
    # Added missing comma before heatmap_blob
    cursor.execute('''CREATE TABLE IF NOT EXISTS session_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        end_time TEXT,
        duration REAL,
        total_keys INTEGER,
        total_clicks INTEGER,
        mouse_distance REAL,
        app_jumps INTEGER,
        top_app TEXT,
        average_intensity REAL,
        idle_duration REAL,
        heatmap_blob BLOB
    )''')

    # Safety: Add column if the table already existed without it
    try:
        cursor.execute("ALTER TABLE session_history ADD COLUMN heatmap_blob BLOB")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    conn.close()

# --- INTERACTION TRACKING LOGIC ---
class AttentionMapper:
    def __init__(self):
        self.key_count = 0
        self.click_count = 0
        self.app_switches = 0
        self.last_app = None
        self.start_time = datetime.now()

    def log_interaction(self, s_type):
        if s_type == "KEY": self.key_count += 1
        if s_type == "CLICK": self.click_count += 1
        
        try:
            conn = sqlite3.connect('attention_history.db')
            conn.execute("INSERT INTO interaction_signals (signal_type) VALUES (?)", (s_type,))
            conn.commit()
            conn.close()
        except: pass

    def save_session_with_heatmap(self, session_data, image_binary):
        """
        Saves the final session metrics along with the heatmap image binary.
        """
        try:
            conn = sqlite3.connect('attention_history.db')
            cursor = conn.cursor()
            
            query = """INSERT INTO session_history 
                       (start_time, end_time, duration, total_keys, total_clicks, heatmap_blob) 
                       VALUES (?, ?, ?, ?, ?, ?)"""
            
            # Use sqlite3.Binary to safely pack the raw PNG bytes
            cursor.execute(query, (
                session_data['start'],
                session_data['end'],
                session_data['duration'],
                session_data['keys'],
                session_data['clicks'],
                sqlite3.Binary(image_binary) 
            ))
            
            conn.commit()
            conn.close()
            print("[+] Session and Heatmap saved to SQLite.")
        except Exception as e:
            print(f"[-] Database Error: {e}")

    def start_listeners(self):
        k_listener = keyboard.Listener(on_press=lambda k: self.log_interaction("KEY"))
        m_listener = mouse.Listener(on_click=lambda x,y,b,p: self.log_interaction("CLICK") if p else None)
        k_listener.start()
        m_listener.start()

    def analyze_attention_window(self):
        while True:
            time.sleep(60) 
            active_win = gw.getActiveWindow()
            current_app = active_win.title if active_win else "Desktop"

            if current_app != self.last_app and self.last_app is not None:
                self.app_switches += 1
            
            self.last_app = current_app
            
            total_signals = self.key_count + self.click_count
            state = "IDLE"
            if total_signals > 20 and self.app_switches < 2:
                state = "DEEP_FOCUS"
            elif self.app_switches >= 2:
                state = "FRAGMENTED"
            elif total_signals > 0:
                state = "PASSIVE"

            print(f"[*] State: {state} | Signals: {total_signals} | Switches: {self.app_switches}")
            self.key_count = 0
            self.click_count = 0
            self.app_switches = 0

# --- EXECUTION ---
if __name__ == "__main__":
    init_db()
    mapper = AttentionMapper()
    mapper.start_listeners()
    print("[+] Interaction Listeners Active (Timestamps only)")
    mapper.analyze_attention_window()