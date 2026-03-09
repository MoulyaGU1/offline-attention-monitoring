import os
from flask import jsonify, render_template
import sqlite3

def register_routes(app, orchestrator):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/history")
    def history_page():
        # Renders the history viewing page
        return render_template("history.html")

    @app.route('/api/history')
    def get_history():
    # MUST MATCH THE ORCHESTRATOR PATH EXACTLY
        db_path = r"C:\Users\lenovo\OneDrive\Documents\Desktop\Moulya\attention-mapping-tool\attention_history.db"
    
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    # Select all 11 columns
        cursor.execute('SELECT * FROM session_history ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    

    @app.route("/start-session", methods=["POST"])
    def start():
        return jsonify(orchestrator.start_session())

    @app.route("/status")
    def status():
        return jsonify(orchestrator.get_realtime_status())

    @app.route("/end-session", methods=["POST"])
    def end():
        # Triggers data storage logic in the orchestrator
        report = orchestrator.end_session() 
        return jsonify(report)