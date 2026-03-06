from collections import defaultdict
from datetime import datetime
from threading import Lock
import statistics

class AttentionEngine:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.timeline = defaultdict(int)
        self.lock = Lock()
        self.resolution_seconds = 5  
        self.history_buffer = [] 

        topics = ["keyboard", "mouse_move", "mouse_click", "scroll", "app_switch"]
        for topic in topics:
            self.event_bus.subscribe(topic, self.process_event)

    def process_event(self, event):
        ts = event.get('timestamp') if isinstance(event, dict) else getattr(event, 'timestamp', datetime.now())
        sec_rounded = (ts.second // self.resolution_seconds) * self.resolution_seconds
        time_bucket = ts.replace(second=sec_rounded, microsecond=0)

        with self.lock:
            self.timeline[time_bucket] += 1
            if time_bucket not in self.history_buffer:
                self.history_buffer.append(time_bucket)
                if len(self.history_buffer) > 50: self.history_buffer.pop(0)

    # THIS IS THE MISSING METHOD THAT CAUSED THE ERROR
    def get_attention_timeline(self):
        with self.lock:
            # Convert datetime keys to strings so JSON can handle them
            return {k.strftime('%H:%M:%S'): v for k, v in sorted(self.timeline.items())}

    def get_adaptive_metrics(self):
        with self.lock:
            if not self.timeline:
                return {"state": "Calibrating", "intensity_ratio": 1.0}
            
            recent_values = [self.timeline[pb] for pb in self.history_buffer]
            avg_intensity = statistics.mean(recent_values) if recent_values else 0
            
            now = datetime.now()
            sec_rounded = (now.second // self.resolution_seconds) * self.resolution_seconds
            current_bucket = now.replace(second=sec_rounded, microsecond=0)
            current_val = self.timeline.get(current_bucket, 0)
            
            ratio = current_val / avg_intensity if avg_intensity > 0 else 1.0
            state = "Deep Flow" if ratio > 1.2 else "Stable" if ratio > 0.6 else "Reflective"
            
            return {"state": state, "intensity_ratio": round(ratio, 2)}
    def get_gravity_data(self, events):
        """Helper to call GravityModel from within the engine."""
        from analyzers.gravity_model import GravityModel
        return GravityModel().calculate_gravity(events)