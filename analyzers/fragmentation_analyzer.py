from datetime import datetime

class FragmentationAnalyzer:
    def __init__(self):
        self.last_switch_time = None
        self.last_app = None

    def compute(self, events):
        """
        Calculates 'Switch Friction': The latency between an app switch 
        and the first meaningful interaction in the new context.
        """
        if not events:
            return 0.0

        friction_delays = []
        last_event_time = events[0].get('timestamp') if isinstance(events[0], dict) else events[0].timestamp

        for i in range(1, len(events)):
            current = events[i]
            prev = events[i-1]
            
            curr_type = current.get('event_type') if isinstance(current, dict) else current.event_type
            prev_type = prev.get('event_type') if isinstance(prev, dict) else prev.event_type
            curr_ts = current.get('timestamp') if isinstance(current, dict) else current.timestamp
            prev_ts = prev.get('timestamp') if isinstance(prev, dict) else prev.timestamp

            # Detect a switch followed by an interaction
            if prev_type == "app_switch" and curr_type in ["keyboard", "mouse_click"]:
                delay = (curr_ts - prev_ts).total_seconds()
                friction_delays.append(delay)

        # Returns average 'Attention Residue' in seconds
        return sum(friction_delays) / len(friction_delays) if friction_delays else 0.0