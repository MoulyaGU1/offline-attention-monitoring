def init_db():
    import sqlite3
    conn = sqlite3.connect('attention_history.db')
    # Use the 9-column schema required by your orchestrator
    conn.execute('''
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT, -- MISSING COLUMN FIXED
            duration REAL,
            total_keys INTEGER,
            total_clicks INTEGER,
            mouse_distance REAL,
            app_jumps INTEGER,
            top_app TEXT,
            average_intensity REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("[+] Database Initialized with 'end_time' column.")