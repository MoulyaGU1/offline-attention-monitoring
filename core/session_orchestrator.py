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
        """Processes hardware events, calculates pixel path, and detects Alt+Tab cycling."""
        if not self.session_active:
            return

        # Safe extraction for Objects or Dicts
        e_type = getattr(event, 'event_type', None) or (event.get('event_type') if isinstance(event, dict) else None)
        e_key = str(getattr(event, 'key', '') or (event.get('key', '') if isinstance(event, dict) else '')).lower()

        # A. PHYSICAL PATH: Euclidean distance calculation (Pixels Traversed)
        # Formula: d = sqrt((x2-x1)^2 + (y2-y1)^2)
        if e_type == "mouse_move":
            curr_x = getattr(event, 'x', 0)
            curr_y = getattr(event, 'y', 0)
            if self.last_mouse_pos:
                dist = math.sqrt((curr_x - self.last_mouse_pos[0])**2 + (curr_y - self.last_mouse_pos[1])**2)
                self.total_mouse_distance += dist
            self.last_mouse_pos = (curr_x, curr_y)

        # B. TRUTHFUL ALT+TAB: Supports cycling (detects multiple tabs while Alt is held)
        if e_type == "keyboard":
            if "alt" in e_key:
                self.alt_pressed = True
            elif "tab" in e_key and self.alt_pressed:
                if isinstance(event, dict): 
                    event['event_type'] = 'tab_switch'
                else: 
                    setattr(event, 'event_type', 'tab_switch')
            else:
                # Reset only if a non-Tab key is pressed or Alt is released
                if "tab" not in e_key:
                    self.alt_pressed = False

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

    def end_session(self):
        """Stops listeners and generates the final cognitive report."""
        if not self.session_active:
            return {"status": "no_active_session"}
            
        self.session_active = False
        self.keyboard.stop()
        self.mouse.stop()
        self.scroll.stop()
        self.app.stop()
        
        session_end = datetime.now()
        self.last_mouse_pos = None # Clean up for memory
        
        return self.generate_analysis(session_end)

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
        """Calculates metrics for the dashboard."""
        if not self.session_active or self.session_start is None:
            return {"status": "inactive"}

        # FIX: Calculate duration locally before using it
        now = datetime.now()
        duration_seconds = (now - self.session_start).total_seconds()
        
        # Metric aggregation
        counts = {"keyboard": 0, "tab_switch": 0, "mouse_move": 0, "mouse_click": 0, "app_switch": 0}
        for e in self.events:
            t = getattr(e, 'event_type', None) or (e.get('event_type') if isinstance(e, dict) else None)
            if t in counts: counts[t] += 1

        adaptive = self.attention_engine.get_adaptive_metrics()

        # FIX: Remove 'navigator'. Use the OfflineValidator or a simple boolean check.
        # We let the Frontend (JS) handle the actual "Blue/Green" dot logic.
        return {
            "status": "active",
            "duration": round(duration_seconds, 2),
            "keyboard_events": counts["keyboard"],
            "tab_switches": counts["tab_switch"],
            "mouse_clicks": counts["mouse_click"],
            "mouse_moves": round(self.total_mouse_distance, 1),
            "app_switches": counts["app_switch"],
            "state": adaptive.get("state", "Stable"),
            "intensity_ratio": adaptive.get("intensity_ratio", 1.0),
            "gravity_map": GravityModel().calculate_gravity(self.events),
            "timeline": self.attention_engine.get_attention_timeline(),
            "security": "LOCAL_ENCRYPTED" # Python just confirms the storage mode
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