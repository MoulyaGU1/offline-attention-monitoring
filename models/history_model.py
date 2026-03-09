import sqlite3
import os
from config import settings

def save_history(data):

    if settings.INCOGNITO_MODE:
        return

    # existing save code

def init_db():
    conn = sqlite3.connect('attention_history.db')
    cursor = conn.cursor()
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
            average_intensity REAL
        )
    ''')
    conn.commit()
    conn.close()