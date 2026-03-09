import time

class IdleTracker:
    def __init__(self, event_bus, threshold=5):
        self.event_bus = event_bus
        self.threshold = threshold
        self.last_activity = time.time()
        self.total_idle_time = 0
        self.is_idle = False
        self.last_check_time = time.time() # NEW: Tracks the last pulse

    def reset_timer(self, event=None):
        """Resets the clock when hardware activity is detected."""
        if self.is_idle:
            self.is_idle = False
            self.event_bus.emit("idle_end", {"at": time.time()})
        self.last_activity = time.time()

    def update(self):
        """
        Calculates idle duration locally.
        This must be called in the orchestrator loop.
        """
        now = time.time()
        elapsed_since_activity = now - self.last_activity
        
        # Calculate time passed since the last update() call
        delta_time = now - self.last_check_time
        self.last_check_time = now

        if elapsed_since_activity > self.threshold:
            # User has passed the threshold, start counting seconds
            self.total_idle_time += delta_time
            if not self.is_idle:
                self.is_idle = True
                self.event_bus.emit("idle_start", {"duration": elapsed_since_activity})
        
        return self.is_idle