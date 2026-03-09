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
        """Retrieves the latest sessions from the local node."""
        import sqlite3
        import os
    # Force absolute path to ensure data is read from the project folder
        db_path = os.path.join(os.getcwd(), 'attention_history.db')
    
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        # Order must match the HTML table: Date, Duration, Jumps, Focus, Intensity
            cursor.execute('''
            SELECT start_time, duration, app_jumps, top_app, average_intensity 
            FROM session_history ORDER BY id DESC LIMIT 20
        ''')
            rows = cursor.fetchall()
            conn.close()
            return jsonify(rows)
        except sqlite3.OperationalError:
        # Returns empty list if table doesn't exist yet
            return jsonify([])
    

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