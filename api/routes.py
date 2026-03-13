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

    @app.route("/history")
    def history_page():
        """Fetches all sessions and safely converts Heatmap BLOBs to viewable URLs."""
        db_path = "attention_history.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM session_history ORDER BY id DESC")
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                # Convert row to dictionary for easier key checking
                session_data = dict(row)
                
                # --- MERGED SAFE CHECK ---
                # 1. Checks if column exists in the row
                # 2. Checks if the data inside is not None
                has_blob = 'heatmap_blob' in session_data and session_data['heatmap_blob'] is not None
                
                if has_blob:
                    try:
                        # Convert raw binary to displayable Base64 string
                        encoded_img = base64.b64encode(row['heatmap_blob']).decode('utf-8')
                        session_data['heatmap_url'] = f"data:image/png;base64,{encoded_img}"
                    except Exception as e:
                        print(f"[*] Error encoding blob for session {session_data.get('id')}: {e}")
                        session_data['heatmap_url'] = None
                else:
                    session_data['heatmap_url'] = None
                    
                sessions.append(session_data)
                
            return render_template('history.html', sessions=sessions)
            
        except Exception as e:
            print(f"[!] Database Error in history_page: {e}")
            return render_template('history.html', sessions=[], error="Could not load history.")
        finally:
            conn.close()

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
        # Read the raw binary from the browser's request
            image_binary = request.files['image'].read()
            session_id = request.form.get('session_id')

            conn = sqlite3.connect('attention_history.db')
            cursor = conn.cursor()
        
        # Link the image to the session row created in Step 1
            query = "UPDATE session_history SET heatmap_blob = ? WHERE id = ?"
            cursor.execute(query, (sqlite3.Binary(image_binary), session_id))
        
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"[-] Heatmap Storage Error: {e}")
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