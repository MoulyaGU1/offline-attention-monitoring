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

    @app.route("/api/history")
    def get_history():
        # Fixed indentation for database access
        conn = sqlite3.connect('attention_history.db')
        cursor = conn.cursor()
        # Fetching latest sessions from local storage
        cursor.execute('''
            SELECT start_time, duration, app_jumps, top_app, average_intensity 
            FROM session_history ORDER BY id DESC LIMIT 20
        ''')
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