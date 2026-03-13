import os
import threading
from flask import app, jsonify, render_template, request
import sqlite3
from flask import Blueprint, jsonify, request
from trackers.flow_lock import start_flow_lock
from flask import request, jsonify
import trackers.flow_lock as fl  # Crucial: Import the module alias
# Change your existing import from this:
from trackers.flow_lock import start_flow_lock
from flask import request, jsonify
import threading # Import the module


# To this:

shield_enabled = True

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
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()

        try:
        # 1. Fetch Raw History (Keeping your existing logic)
            cursor.execute('SELECT * FROM session_history ORDER BY id DESC')
            rows = cursor.fetchall()

        # 2. Existing Distribution/Summary Logic
            if session_id and session_id != 'all':
                cursor.execute('SELECT * FROM session_history WHERE id = ?', (session_id,))
                graph_rows = cursor.fetchall()
                dist_data = [{"app_name": r[8], "total_duration": r[3]} for r in graph_rows]
            else:
                cursor.execute('SELECT * FROM session_history')
                all_data = cursor.fetchall()
                summary = {}
                for r in all_data:
                    name = r[8] if r[8] else "Unknown"
                    duration = r[3] if r[3] else 0
                    summary[name] = summary.get(name, 0) + duration
                dist_data = [{"app_name": k, "total_duration": v} for k, v in summary.items()]
                dist_data = sorted(dist_data, key=lambda x: x['total_duration'], reverse=True)

        # --- NEW: ADDING COMPLIANCE DATA (Heatmap & States) ---
        # We transform the existing 'rows' to include Mandatory Features
            formatted_raw = []
            heatmap_data = []
            for r in rows:
            # Interaction density (Keys + Clicks)
                density = (r[4] if r[4] else 0) + (r[5] if r[5] else 0)
            
            # Map Attention State (Constraint: No Judgment, just state identification)
                state = "DEEP_FOCUS"
                if (r[7] if r[7] else 0) > 2: state = "FRAGMENTED" # Based on app_jumps
                if density == 0: state = "IDLE"

                formatted_raw.append({
                    "id": r[0],
                    "time": r[1],
                    "duration": r[3],
                    "interaction_density": density,
                    "fragmentation_index": r[7], # app_jumps
                    "attention_state": state,
                    "top_app": r[8]
                })
            
            # Populate Heatmap (Density over time)
                heatmap_data.append({"t": r[1], "v": density})

            conn.close()

        # Merged Return: Existing structure + New Compliance keys
            return jsonify({
                "distribution": dist_data,
                "raw_history": [list(row) for row in rows], # Keeping your original format
                "formatted_history": formatted_raw,         # New mandatory feature data
                "heatmap": heatmap_data[::-1],              # Reversed for chronological chart
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
    @app.route('/api/start_lock', methods=['POST'])
    def start_lock():
        try:
            data = request.json
            target_app = data.get('target_app', 'Visual Studio Code')
            duration = data.get('duration', 30)
        
        # Launch lock in a separate thread so Flask doesn't hang
            thread = threading.Thread(target=start_flow_lock, args=(target_app, duration))
            thread.daemon = True
            thread.start()
        
            return jsonify({"status": "success", "message": f"Locking to {target_app}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    @app.route('/api/data', methods=['GET'])
    def get_live_data():
        try:
        # Pull real-time counts from your engine
        # If your engine uses a different name, adjust accordingly
            metrics = orchestrator.get_realtime_status() 
        
            return jsonify({
                "status": "success",
                "active_app": metrics.get('active_app', 'System'),
                "keyboard_count": metrics.get('keyboard', 0),
                "mouse_count": metrics.get('mouse', 0),
                "intensity": metrics.get('intensity', 0.0)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
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
    
    

    @app.route('/api/toggle_shield', methods=['POST'])
    def toggle_shield():
        global shield_enabled
        data = request.json
        shield_enabled = data.get('enabled', True)
        return jsonify({"status": "success", "shield_active": shield_enabled})
    @app.route('/api/flow/pause', methods=['POST'])
    def pause_shield():
        data = request.json
    # This directly changes the variable the 'while' loop is watching
        fl.IS_PAUSED = data.get('paused', False) 
        return jsonify({"status": "success", "paused": fl.IS_PAUSED})

    @app.route('/api/flow/stop', methods=['POST'])
    def stop_shield():
    # This triggers the 'break' in the 'while' loop
        fl.FORCE_STOP = True 
        return jsonify({"status": "terminated"})
    @app.route('/engage_history')
    def engage_history_page():
        # This renders the HTML file you created for history
        return render_template('history.html') 

    @app.route('/api/engage/history', methods=['GET'])
    def get_engage_data():
    # This provides the actual data to the page
        conn = sqlite3.connect('attention_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM engage_history ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    # In routes.py
    import threading # Ensure this is imported at the top of routes.py

    # api/routes.py
    # api/routes.py
    def generate_attention_fingerprint(timeline_data):
        """
        Converts raw timeline data into a 'Fingerprint' string.
        Example: [{"time": "10:01", "val": 0.9}, ...] -> "Focus 10m -> Drift -> Focus 5m"
        """
        if not timeline_data:
            return "No Data Recorded"

        fingerprint_steps = []
        current_state = None
        duration_counter = 0

        for entry in timeline_data:
            val = entry.get('val', 0)
        # Determine State
            if val >= 0.8:
                state = "Deep Focus"
            elif 0.3 <= val < 0.8:
                state = "Switching"
            else:
                state = "Idle/Drift"

            if state == current_state:
                duration_counter += 1
            else:
                if current_state:
                    fingerprint_steps.append(f"{current_state} ({duration_counter}s)")
                current_state = state
                duration_counter = 1

    # Add final state
        fingerprint_steps.append(f"{current_state} ({duration_counter}s)")
    
    # Return as DNA string
        return " ➔ ".join(fingerprint_steps)


    