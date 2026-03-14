import os
import sqlite3
import base64
import threading
from flask import render_template, request, jsonify
import datetime

# --- TRACKER IMPORTS ---
import trackers.flow_lock as fl
from trackers.flow_lock import start_flow_lock

# Global variable for shield state
shield_enabled = True

def register_routes(app, orchestrator):
    """
    Registers all routes for the Attention Engine.
    'app' is the Flask instance, 'orchestrator' is the tracking engine.
    """

    # --- 1. PAGE RENDERING ROUTES ---

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/analytics")
    def analytics_page():
        """Dedicated route for the Graph Selection & Pattern Analysis."""
        return render_template("analytics.html")

    @app.route('/api/history')
    def get_history():
        session_id = request.args.get('id')
        db_path = r"C:\Users\lenovo\OneDrive\Documents\Desktop\Moulya\attention-mapping-tool\attention_history.db"

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM session_history ORDER BY id DESC')
            rows = cursor.fetchall()
        
            processed_history = []
            session_dropdown_list = []

            for r in rows:
                d = dict(r)
                session_dropdown_list.append({
                    "id": d.get('id'),
                    "time": d.get('start_time') or d.get('start')
                })

                if d.get('heatmap_blob'):
                    try:
                        encoded = base64.b64encode(d['heatmap_blob']).decode('utf-8')
                        d['heatmap_url'] = f"data:image/png;base64,{encoded}"
                    except Exception:
                        d['heatmap_url'] = None
                else:
                    d['heatmap_url'] = None
            
                if 'heatmap_blob' in d: del d['heatmap_blob']
                processed_history.append(d)

        # --- DYNAMIC DISTRIBUTION LOGIC ---
            dist_data = []
            selected = None

            if session_id and session_id != 'all':
            # VIEW 1: Specific Session -> Show app breakdown for THIS session
                selected = next((s for s in processed_history if str(s['id']) == str(session_id)), None)
                if selected:
                # If your DB only stores 'top_app', we show that. 
                # If you have multiple apps per session, you'd iterate here.
                    dist_data = [{"app_name": selected.get('top_app', 'Unknown'), "total_duration": selected.get('duration', 0)}]
            else:
            # VIEW 2: All-Time Overview -> Show comparison of ALL sessions
            # This makes the graph change significantly when switching from 'All' to a 'Specific ID'
                dist_data = [
                    {
                        "app_name": f"Sess #{s['id']}", 
                        "total_duration": s.get('duration', 0)
                    } for s in processed_history
                ]

            return jsonify({
                "status": "success",
                "distribution": dist_data,
                "raw_history": processed_history,
                "session_list": session_dropdown_list,
                "selected_session": selected
            })

        except Exception as e:
            print(f"SQL Error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            if conn: conn.close()
    @app.route('/engage_history')
    def engage_history_page():
        return render_template('history.html') 

    # --- 2. SESSION CONTROL API ---

    @app.route("/start-session", methods=["POST"])
    def start():
        return jsonify(orchestrator.start_session())

    @app.route("/status")
    def status():
        return jsonify(orchestrator.get_realtime_status())

    @app.route("/end-session", methods=["POST"])
    def end():
        report = orchestrator.end_session() 
        return jsonify(report)

    @app.route('/api/data', methods=['GET'])
    def get_live_data():
        try:
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

    # --- 3. HEATMAP & ANALYTICS API ---

    @app.route("/history")
    def history_page():
        """Renders the HTML page for session history."""
        try:
        # We don't need to do the heavy lifting here because 
        # the frontend JS (loadHistory) will call /api/history to get the data.
            return render_template("history.html")
        except Exception as e:
            return f"Error loading history page: {e}", 500
   
        

    @app.route('/api/start_lock', methods=['POST'])
    def start_lock():
        try:
            data = request.json
            target_app = data.get('target_app', 'Visual Studio Code')
            duration = data.get('duration', 30)
            thread = threading.Thread(target=start_flow_lock, args=(target_app, duration))
            thread.daemon = True
            thread.start()
            return jsonify({"status": "success", "message": f"Locking to {target_app}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/toggle_shield', methods=['POST'])
    def toggle_shield():
        global shield_enabled
        data = request.json
        shield_enabled = data.get('enabled', True)
        return jsonify({"status": "success", "shield_active": shield_enabled})

    @app.route('/api/flow/pause', methods=['POST'])
    def pause_shield():
        data = request.json
        fl.IS_PAUSED = data.get('paused', False) 
        return jsonify({"status": "success", "paused": fl.IS_PAUSED})

    @app.route('/api/flow/stop', methods=['POST'])
    def stop_shield():
        fl.FORCE_STOP = True 
        return jsonify({"status": "terminated"})

    @app.route('/api/engage/history', methods=['GET'])
    def get_engage_data():
        conn = sqlite3.connect('attention_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM engage_history ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

# --- HELPER LOGIC ---
    def generate_attention_fingerprint(timeline_data):
        if not timeline_data: return "No Data Recorded"
        fingerprint_steps = []
        current_state = None
        duration_counter = 0

        for entry in timeline_data:
            val = entry.get('val', 0)
            state = "Deep Focus" if val >= 0.8 else ("Switching" if 0.3 <= val < 0.8 else "Idle/Drift")

            if state == current_state:
                duration_counter += 1
            else:
                if current_state: fingerprint_steps.append(f"{current_state} ({duration_counter}s)")
                current_state = state
                duration_counter = 1
        fingerprint_steps.append(f"{current_state} ({duration_counter}s)")
        return " ➔ ".join(fingerprint_steps)
    @app.route('/api/store_heatmap_blob', methods=['POST'])
    def store_heatmap_blob():
        try:
        # 1. Get binary image and session ID from the request
            image_bytes = request.files['image'].read()
            session_id = request.form.get('session_id')

            db_path = "attention_history.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        
        # 2. Store as binary (sqlite3.Binary handles the conversion)
            cursor.execute("UPDATE session_history SET heatmap_blob = ? WHERE id = ?", 
                       (sqlite3.Binary(image_bytes), session_id))
        
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    def end_session(self):
        """Finalizes the session and returns the ID for the Heatmap."""
        if not self.session_active:
            return {"status": "error", "message": "No active session"}

        try:
            # 1. Prepare the data package
            session_end = datetime.now()
            duration = round((session_end - self.session_start).total_seconds(), 2)
            
            db_data = {
                "start": self.session_start.strftime('%Y-%m-%d %H:%M:%S'),
                "end": session_end.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": duration,
                "keys": self.key_count, # Use your tracking variables
                "clicks": self.click_count,
                "dist": round(self.total_mouse_distance, 1),
                "switches": self.app_switches,
                "gravity": self.last_app or "General",
                "density": 1.0,
                "recovery": 0.0
            }

            # 2. Save to DB and get the ID
            new_session_id = self.save_to_local_db(db_data)
            
            self.session_active = False 
            
            if new_session_id:
                # CRITICAL: Return the ID so JS can use it
                return {"status": "success", "session_id": new_session_id}
            else:
                return {"status": "error", "message": "Failed to generate session ID"}

        except Exception as e:
            print(f"[-] End Session Error: {e}")
            return {"status": "error"}