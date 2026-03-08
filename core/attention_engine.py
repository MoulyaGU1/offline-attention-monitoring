import datetime

# Ensure there is NO indentation before 'class'
class AttentionEngine:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.timeline = {}  # Stores {datetime: count}
        self.last_score = 1.0

    def process_event(self, data):
        # Use datetime.datetime.now() to avoid attribute errors
        now = datetime.datetime.now().replace(microsecond=0)
        if now not in self.timeline:
            self.timeline[now] = 0
        self.timeline[now] += 1

    def update(self, events):
        """Calculates a dynamic, pulsing score for the Topology Graph."""
        import datetime
        now = datetime.datetime.now().replace(microsecond=0)
        
        # 1. Burst Window: Look only at activity from the last 1.5 seconds
        burst_threshold = datetime.datetime.now() - datetime.timedelta(seconds=1.5)
        
        # Identify how many events happened 'right now'
        burst_activity = sum(1 for e in events if (getattr(e, 'timestamp', datetime.datetime.now()) 
                             if not isinstance(e, dict) else e.get('timestamp', datetime.datetime.now())) > burst_threshold)
        
        # 2. Dynamic Score: 
        # Visible baseline floor is 0.4. Each recent event adds 0.2 height.
        target_score = 0.4 + (burst_activity * 0.2)
        
        # 3. Cap at 2.0 to fit the Chart.js Y-axis scale
        self.last_score = min(2.0, target_score)
        
        # 4. Save to timeline dictionary
        self.timeline[now] = self.last_score
    def get_attention_timeline(self):
        formatted = {}
        try:
            # Sort by time so the graph draws left-to-right
            for k in sorted(self.timeline.keys()):
                v = self.timeline[k]
                # Convert datetime object to "17:30:05" string
                time_str = k.strftime('%H:%M:%S') if hasattr(k, 'strftime') else str(k)
                formatted[time_str] = v
            
            # Return last 60 seconds
            recent = list(formatted.keys())[-60:]
            return {k: formatted[k] for k in recent}
        except Exception:
            return {}

    def get_adaptive_metrics(self):
        """Returns the current cognitive state based on recent intensity."""
        state = "Deep Flow" if self.last_score > 1.2 else "Reflective"
        if self.last_score < 0.4: state = "Idle"
        
        return {
            "state": state,
            "intensity_ratio": round(self.last_score, 2)
        }