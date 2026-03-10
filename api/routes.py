import os
from flask import app, jsonify, render_template, request
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
        session_id = request.args.get('id')
        db_path = r"C:\Users\lenovo\OneDrive\Documents\Desktop\Moulya\attention-mapping-tool\attention_history.db"

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Allow access by column name
        cursor = conn.cursor()

        try:
        # 1. Fetch Raw History for the table (always show all columns)
            cursor.execute('SELECT * FROM session_history ORDER BY id DESC')
            rows = cursor.fetchall()
    
        # 2. Logic for the Graph (Distribution)
        # We use column index r[8] for app_name and r[3] for duration to be safe
            if session_id and session_id != 'all':
                cursor.execute('SELECT * FROM session_history WHERE id = ?', (session_id,))
                graph_rows = cursor.fetchall()
            # If filtering by ID, just take the app name and duration from that row
                dist_data = [{"app_name": r[8], "total_duration": r[3]} for r in graph_rows]
            else:
            # Global Summary: We calculate the sum manually to avoid column name errors
                cursor.execute('SELECT * FROM session_history')
                all_data = cursor.fetchall()
        
            # Helper to group by app name manually
                summary = {}
                for r in all_data:
                    name = r[8] if r[8] else "Unknown"
                    duration = r[3] if r[3] else 0
                    summary[name] = summary.get(name, 0) + duration
        
                dist_data = [{"app_name": k, "total_duration": v} for k, v in summary.items()]
            # Sort by highest duration
                dist_data = sorted(dist_data, key=lambda x: x['total_duration'], reverse=True)

            conn.close()

            return jsonify({
                "distribution": dist_data,
                "raw_history": [list(row) for row in rows],
                "session_list": [{"id": r[0], "time": r[1]} for r in rows]
            })

        except Exception as e:
            if conn: conn.close()
            print(f"SQL Error: {e}")
            return jsonify({"error": str(e)}), 500
    @app.route("/analytics")
    def analytics_page():
        """Dedicated route for the Graph Selection & Pattern Analysis."""
        return render_template("analytics.html")

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