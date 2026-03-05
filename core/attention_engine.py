from collections import defaultdict
from datetime import datetime
from threading import Lock

class AttentionEngine:
    """
    Core engine that processes interaction signals
    and builds a real-time attention timeline.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.timeline = defaultdict(int)
        self.lock = Lock()

        # subscribe to interaction events
        self.event_bus.subscribe("keyboard", self.process_event)
        self.event_bus.subscribe("mouse_move", self.process_event)
        self.event_bus.subscribe("mouse_click", self.process_event)
        self.event_bus.subscribe("scroll", self.process_event)
        self.event_bus.subscribe("app_switch", self.process_event)

    def process_event(self, event):
        """Processes events and buckets them by the minute."""
        # 1. Safe extraction of timestamp (Handle Dict or Object)
        if isinstance(event, dict):
            ts = event.get('timestamp')
        else:
            ts = getattr(event, 'timestamp', None)

        # 2. Fallback to current time if timestamp is missing or invalid
        if not isinstance(ts, datetime):
            ts = datetime.now()

        # 3. Create the minute bucket
        minute_bucket = ts.replace(second=0, microsecond=0)

        with self.lock:
            self.timeline[minute_bucket] += 1

    def get_attention_timeline(self):
        with self.lock:
            # Sort by time so the timeline makes sense when printed
            return dict(sorted(self.timeline.items()))

    def get_current_attention_score(self):
        """Returns attention intensity of the current minute."""
        now = datetime.now().replace(second=0, microsecond=0)
        with self.lock:
            return self.timeline.get(now, 0)