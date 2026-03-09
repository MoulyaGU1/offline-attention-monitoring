import sqlite3
import os

def init_db():
    db_path = os.path.join(os.getcwd(), 'attention_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Clear old version to avoid 'Column Not Found' errors
    cursor.execute("DROP TABLE IF EXISTS session_history")
    
    # 2. Create the 11-column table
    cursor.execute('''
        CREATE TABLE session_history (
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
            idle_duration REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[+] Database Initialized at: {db_path}")

# Run this once when you start the app
init_db()