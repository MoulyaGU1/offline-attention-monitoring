import math
import threading
import os
import time
from datetime import datetime
from utils.logger import Logger
from core.event_bus import EventBus
from core.attention_engine import AttentionEngine
from trackers.keyboard_tracker import KeyboardTracker
from trackers.mouse_tracker import MouseTracker
from trackers.scroll_tracker import ScrollTracker
from trackers.app_tracker import AppTracker
from trackers.idle_tracker import IdleTracker
from analyzers.stability_analyzer import StabilityAnalyzer
from reports.session_report_generator import ReportGenerator
from analyzers.gravity_model import GravityModel
from core.offline_validator import OfflineValidator
# Should be exactly this:
from core.attention_engine import AttentionEngine
import sqlite3

class SessionOrchestrator:
    def __init__(self):
        # 1. Initialize Logger & core components
        self.logger = Logger.get_logger()
        self.event_bus = EventBus()
        self.attention_engine = AttentionEngine(self.event_bus)

        # 2. Trackers
        self.keyboard = KeyboardTracker(self.event_bus)
        self.mouse = MouseTracker(self.event_bus)
        self.scroll = ScrollTracker(self.event_bus)
        self.app = AppTracker(self.event_bus)
        self.idle = IdleTracker(self.event_bus)

        # 3. Analyzers & Path Tracking
        self.stability = StabilityAnalyzer()
        self.report_generator = ReportGenerator()
        self.last_mouse_pos = None
        self.total_mouse_distance = 0

        # 4. State Variables
        self.session_active = False
        self.session_start = None
        self.events = []
        self.alt_pressed = False 

        # 5. Subscriptions
        self.event_bus.subscribe("keyboard", self.capture_event)
        self.event_bus.subscribe("mouse_move", self.capture_event)
        self.event_bus.subscribe("mouse_click", self.click_event)
        self.event_bus.subscribe("scroll", self.capture_event)
        self.event_bus.subscribe("app_switch", self.capture_event)

    def capture_event(self, event):
        """
        Unified Event Processor: 
        Handles metadata extraction, Physical Path (Pixels), Alt+Tab switching, 
        and Dashboard filtering.
        """
        if not self.session_active:
            return

        # 1. ROBUST IDENTIFICATION (Object vs Dictionary)
        if isinstance(event, dict):
            e_type = event.get('event_type')
            e_key = str(event.get('key', '')).lower()
            # Deep metadata check for app name
            app_name = str(event.get('app_name') or event.get('metadata', {}).get('app', 'Unknown')).lower()
        else:
            e_type = getattr(event, 'event_type', None)
            e_key = str(getattr(event, 'key', '')).lower()
            # Deep attribute check for app name
            app_name = str(getattr(event, 'app_name', None) or getattr(event, 'metadata', {}).get('app', 'Unknown')).lower()

        # 2. DASHBOARD FILTER (Strict Exclusion)
        # Prevents the tool from tracking its own switches/clicks
        is_dashboard = any(x in app_name for x in ["Attention Mapping", "127.0.0.1", "localhost", "chrome-extension"])

        # 3. PHYSICAL PATH MATH (Euclidean distance)
        if e_type == "mouse_move":
            curr_x = event.get('x', 0) if isinstance(event, dict) else getattr(event, 'x', 0)
            curr_y = event.get('y', 0) if isinstance(event, dict) else getattr(event, 'y', 0)
            
            if self.last_mouse_pos:
                # Calculate √((x2-x1)² + (y2-y1)²)
                dist = math.sqrt((curr_x - self.last_mouse_pos[0])**2 + (curr_y - self.last_mouse_pos[1])**2)
                self.total_mouse_distance += dist
            self.last_mouse_pos = (curr_x, curr_y)

        # 4. TRUTHFUL APP JUMPS (Filtering out the Dashboard)
        if e_type == "app_switch":
            # Extract name and filter out the dashboard
            name = getattr(event, 'app_name', None) or event.get('app_name', 'Unknown')
            if any(x in name.lower() for x in ["Attention Mapping", "127.0.0.1"]):
                return # Ignore dashboard
            self.current_app = name

        # 5. TRUTHFUL ALT+TAB (Cycling Support)
        if e_type == "keyboard":
            if "alt" in e_key:
                self.alt_pressed = True
            elif "tab" in e_key and self.alt_pressed:
                # Re-categorize as a tab switch so it doesn't count as a jump or keypress
                if isinstance(event, dict): event['event_type'] = 'tab_switch'
                else: setattr(event, 'event_type', 'tab_switch')
            else:
                # Reset if any non-Tab key is hit
                if "tab" not in e_key:
                    self.alt_pressed = False

        # 6. FINAL STORAGE
        self.events.append(event)

    def click_event(self, event):
        """Dedicated handler to label mouse clicks correctly for the UI."""
        if self.session_active:
            if isinstance(event, dict): 
                event['event_type'] = 'mouse_click'
            else: 
                setattr(event, 'event_type', 'mouse_click')
            self.events.append(event)

    def start_session(self):
        """Starts hardware listeners and resets session-specific metrics."""
        if self.session_active:
            return {"status": "already_running"}
        
        self.logger.info("Attention Mapping Session Started")
        self.session_active = True
        self.session_start = datetime.now()
        self.events = []
        self.total_mouse_distance = 0 
        self.last_mouse_pos = None # Reset starting position for new session
        
        # Start hardware listeners
        self.keyboard.start()
        self.mouse.start()
        self.scroll.start()
        self.app.start()
        
        # Ensure the AppTracker (which usually polls) runs in its own thread
        if hasattr(self.app, 'run'):
            threading.Thread(target=self.app.run, daemon=True).start()
        
        return {"status": "session_started"}

    def get_realtime_status(self):
        """Aggregates metrics for the dashboard.js frontend."""
        if not self.session_active or self.session_start is None:
            return {"status": "inactive"}

        now = datetime.now()
        duration = (now - self.session_start).total_seconds()
        
        # Aggregate counts safely across different event types
        counts = {"keyboard": 0, "tab_switch": 0, "mouse_move": 0, "mouse_click": 0, "app_switch": 0}
        for e in self.events:
            t = getattr(e, 'event_type', None) or (e.get('event_type') if isinstance(e, dict) else None)
            if t in counts: 
                counts[t] += 1

        adaptive = self.attention_engine.get_adaptive_metrics()

        return {
            "status": "active",
            "duration": round(duration, 2),
            "keyboard_events": counts["keyboard"],
            "tab_switches": counts["tab_switch"],
            "mouse_clicks": counts["mouse_click"],
            "mouse_moves": round(self.total_mouse_distance, 1), # Physical Path in Pixels
            "app_switches": counts["app_switch"],
            "state": adaptive.get("state", "Stable"),
            "intensity_ratio": adaptive.get("intensity_ratio", 1.0),
            "gravity_map": GravityModel().calculate_gravity(self.events),
            "timeline": self.attention_engine.get_attention_timeline(),
            "security": OfflineValidator().get_security_status()
        }

    def get_manual_gravity(self):
        """Helper to identify app usage from the current event list."""
        gravity_stats = {}
        for e in self.events:
            # Check both object attributes and dictionary keys
            name = getattr(e, 'app_name', None) or (e.get('app_name') if isinstance(e, dict) else None)
            if name and name not in ["Unknown", "", "Attention Mapping", "127.0.0.1", "localhost"]:
                gravity_stats[name] = gravity_stats.get(name, 0) + 1
        return gravity_stats

    def end_session(self):
        """Finalizes metrics and triggers the SQL storage command."""
        if not self.session_active:
            return None

        # 1. Capture final time and duration
        end_time = datetime.now()
        duration = (end_time - self.session_start).total_seconds()

        # 2. Extract specific counts for the Database
        counts = {"keyboard": 0, "mouse_click": 0, "app_switch": 0}
        for e in self.events:
            t = getattr(e, 'event_type', None) or (e.get('event_type') if isinstance(e, dict) else None)
            if t in counts: 
                counts[t] += 1

        # 3. Determine the Top App (Identify focus from Gravity Map)
        gravity = self.get_manual_gravity()
        top_app = max(gravity, key=gravity.get) if gravity else "None"
        
        # 4. Calculate Average Intensity
        timeline_values = list(self.attention_engine.timeline.values())
        avg_intensity = sum(timeline_values) / len(timeline_values) if timeline_values else 0.4

        # 5. TRIGGER STORAGE
        self.save_to_local_db({
            "start": self.session_start.strftime('%Y-%m-%d %H:%M:%S'),
            "end": end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "duration": round(duration, 2),
            "keys": counts["keyboard"],
            "clicks": counts["mouse_click"],
            "dist": round(self.total_mouse_distance, 1),
            "jumps": counts["app_switch"],
            "top_app": top_app,
            "intensity": round(avg_intensity, 2)
        })

        self.session_active = False
        self.events = [] # Clear memory for next session
        return {"status": "stored", "duration": duration}

    def save_to_local_db(self, data):
        """Executes the SQL INSERT command with explicit commit."""
        try:
            conn = sqlite3.connect('attention_history.db')
            cursor = conn.cursor()
            # Ensure the number of '?' matches your table columns
            cursor.execute('''
                INSERT INTO session_history 
                (start_time, end_time, duration, total_keys, total_clicks, mouse_distance, app_jumps, top_app, average_intensity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['start'], data['end'], data['duration'], data['keys'], 
                  data['clicks'], data['dist'], data['jumps'], data['top_app'], data['intensity']))
            conn.commit()  # This saves the data to the disk
            conn.close()
            print(f"[+] Session persisted to local DB: {data['top_app']}")
        except Exception as e:
            print(f"[-] Database Error: {e}")
    def generate_analysis(self, session_end):
        """Computes the final Stability Score and generates the full analysis report."""
        report = self.report_generator.generate(self.events)
        
        # Calculate final metrics for the report
        duration = round((session_end - self.session_start).total_seconds(), 2)
        timeline = self.attention_engine.get_attention_timeline()
        stability = self.stability.compute(timeline)
        
        report.update({
            "status": "session_ended",
            "duration": duration,
            "final_state": self.attention_engine.get_adaptive_metrics().get("state", "Unknown"),
            "stability_score": stability
        })
        return report
    def get_realtime_status(self):
        if not self.session_active or self.session_start is None:
            return {"status": "inactive"}

        # 1. GENERATE THE GRAPH POINTS
        self.attention_engine.update(self.events)

        # 2. MANUAL GRAVITY CALCULATION (More reliable than the model)
        gravity_stats = {}
        for e in self.events:
            # Extract app name from object or dictionary
            name = getattr(e, 'app_name', None) or (e.get('app_name') if isinstance(e, dict) else None)
            # Ignore the dashboard and 'Unknown'
            if name and name != "Unknown" and name != "":
                gravity_stats[name] = gravity_stats.get(name, 0) + 1

        # 3. COUNTER LOGIC (As you already wrote)
        counts = {"keyboard": 0, "tab_switch": 0, "mouse_click": 0, "app_switch": 0}
        for e in self.events:
            t = getattr(e, 'event_type', None) or (e.get('event_type') if isinstance(e, dict) else None)
            if t in counts: 
                counts[t] += 1

        # 4. FINAL PAYLOAD
        return {
            "status": "active",
            "duration": round((datetime.now() - self.session_start).total_seconds(), 2),
            "keyboard_events": counts["keyboard"],
            "mouse_clicks": counts["mouse_click"],
            "mouse_moves": round(self.total_mouse_distance, 1),
            "tab_switches": counts["tab_switch"],
            "app_switches": counts["app_switch"],
            "gravity_map": gravity_stats,  # Sends real app names
            "timeline": self.attention_engine.get_attention_timeline(), # The graph line
            "intensity_ratio": round(self.attention_engine.last_score, 2),
            "state": self.attention_engine.get_adaptive_metrics().get("state", "Stable")
            
        }
# --- REAL-TIME CLI EXECUTION BLOCK ---
if __name__ == "__main__":
    orchestrator = SessionOrchestrator()
    orchestrator.start_session()
    try:
        while True:
            stats = orchestrator.get_realtime_status()
            # Clear console for the dashboard look
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=== REAL-TIME COGNITIVE MONITOR ===")
            for key, val in stats.items():
                if key != "timeline" and key != "gravity_map": # Don't flood CLI with raw data
                    print(f"{key:18} : {val}")
            
            time.sleep(0.5) # Refresh rate
    except KeyboardInterrupt:
        final_report = orchestrator.end_session()
        print("\n[!] Session Finished. Data Encrypted and Saved.")