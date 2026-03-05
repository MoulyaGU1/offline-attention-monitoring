from core.event_bus import EventBus
from core.attention_engine import AttentionEngine
from trackers.keyboard_tracker import KeyboardTracker
from trackers.mouse_tracker import MouseTracker
from trackers.scroll_tracker import ScrollTracker
from trackers.app_tracker import AppTracker
from trackers.idle_tracker import IdleTracker
from analyzers.stability_analyzer import StabilityAnalyzer
from analyzers.pattern_detector import PatternDetector
from analyzers.fragmentation_analyzer import FragmentationAnalyzer
from reports.session_report_generator import ReportGenerator
from utils.logger import Logger
from datetime import datetime
import threading
import os

# ... (imports remain the same)

class SessionOrchestrator:
    def __init__(self):
        self.logger = Logger.get_logger()
        self.event_bus = EventBus()
        self.attention_engine = AttentionEngine(self.event_bus)

        self.keyboard = KeyboardTracker(self.event_bus)
        self.mouse = MouseTracker(self.event_bus)
        self.scroll = ScrollTracker(self.event_bus)
        self.app = AppTracker(self.event_bus)
        self.idle = IdleTracker(self.event_bus)

        self.stability = StabilityAnalyzer()
        self.pattern = PatternDetector()
        self.fragmentation = FragmentationAnalyzer()
        self.report_generator = ReportGenerator()

        self.session_active = False
        self.session_start = None
        self.events = []

        self.event_bus.subscribe("keyboard", self.capture_event)
        self.event_bus.subscribe("mouse_move", self.capture_event)
        self.event_bus.subscribe("mouse_click", self.capture_event)
        self.event_bus.subscribe("scroll", self.capture_event)
        self.event_bus.subscribe("app_switch", self.capture_event)

    def capture_event(self, event):
        if self.session_active:
            self.events.append(event)

    def click_event(self, event):
        if self.session_active:
            # Handle if event is a dict or object
            if isinstance(event, dict):
                event['event_type'] = 'mouse_click'
            else:
                setattr(event, 'event_type', 'mouse_click')
            self.events.append(event)

    def start_session(self):
        if self.session_active:
            return {"status": "already_running"}
        self.logger.info("Session started")
        self.session_active = True
        self.session_start = datetime.now()
        self.events = []
        self.keyboard.start()
        self.mouse.start()
        self.scroll.start()
        self.app.start()
        threading.Thread(target=self.app.run, daemon=True).start()
        return {"status": "session_started"}

    # FIX: Indented this method correctly inside the class
    def get_realtime_status(self):
        """Calculates metrics from the current event buffer without stopping."""
        if not self.session_active or self.session_start is None:
            return {"status": "inactive"}

        now = datetime.now()
        duration = (now - self.session_start).total_seconds()
        
        kb_count = 0
        m_moves = 0
        m_clicks = 0
        app_sw = 0

        for e in self.events:
            # This is the "Safety Pipe": check for object attribute OR dictionary key
            e_type = getattr(e, 'event_type', None) or (e.get('event_type') if isinstance(e, dict) else None)
            
            if e_type == "keyboard": kb_count += 1
            elif e_type == "mouse_move": m_moves += 1
            elif e_type == "mouse_click": m_clicks += 1
            elif e_type == "app_switch": app_sw += 1

        timeline = self.attention_engine.get_attention_timeline()
        formatted_timeline = {str(k): v for k, v in timeline.items()}

        return {
            "app_switches": app_sw,
            "duration": round(duration, 4),
            "fragmentation": self.fragmentation.compute(self.events),
            "keyboard_events": kb_count,
            "mouse_clicks": m_clicks,
            "mouse_moves": m_moves,
            "patterns": self.pattern.detect(self.events),
            "stability": self.stability.compute(formatted_timeline),
            "timeline": formatted_timeline
        }

    def end_session(self):
        if not self.session_active:
            return {"status": "no_active_session"}
        self.session_active = False
        self.keyboard.stop()
        self.mouse.stop()
        self.scroll.stop()
        self.app.stop()
        session_end = datetime.now()
        return self.generate_analysis(session_end)

    def generate_analysis(self, session_end):
        duration = (session_end - self.session_start).total_seconds()
        attention_timeline = self.attention_engine.get_attention_timeline()
        attention_timeline = {str(k): v for k, v in attention_timeline.items()}
        report = self.report_generator.generate(self.events)
        report.update({
            "duration": duration,
            "stability": self.stability.compute(attention_timeline),
            "fragmentation": self.fragmentation.compute(self.events),
            "patterns": self.pattern.detect(self.events),
            "timeline": attention_timeline
        })
        return report

# ... (execution block remains the same)
# --- REAL-TIME EXECUTION BLOCK ---
if __name__ == "__main__":
    orchestrator = SessionOrchestrator()
    orchestrator.start_session()
    
    try:
        while True:
            stats = orchestrator.get_realtime_status()
            # Clear console for that "real-time dashboard" look
            os.system('cls' if os.name == 'nt' else 'clear')
            
            for key, val in stats.items():
                print(f"{key:16} : {val}")
                
            import time
            time.sleep(0.5) # Refresh every half second
    except KeyboardInterrupt:
        final_report = orchestrator.end_session()
        print("\nSession Finished.")