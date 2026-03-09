import sys
import sqlite3
from api.server import start_server

def init_db():
    import sqlite3
    import os
    db_path = r"C:\Users\lenovo\OneDrive\Documents\Desktop\Moulya\attention-mapping-tool\attention_history.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # REMOVE: cursor.execute("DROP TABLE IF EXISTS session_history") 
    # USE THIS INSTEAD:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_history (
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
    print(f"[+] Local Repository Synced. Previous sessions preserved.")
if __name__ == "__main__":
    print("==============================================")
    print("🧠 OFFLINE ATTENTION MAPPING TOOL: WEB MODE")
    print("==============================================")
    print("1. Open your browser to: http://127.0.0.1:5000")
    print("2. Click 'START SESSION' on the website.")
    print("3. Use your computer normally to see the data.")
    print("----------------------------------------------")
    
    # Initialize the database before starting the server
    init_db() 
    
    try:
        # Start the Flask server (this is your backend)
        start_server()
    except KeyboardInterrupt:
        print("\n[!] Shutting down mapping engine...")
        sys.exit(0)