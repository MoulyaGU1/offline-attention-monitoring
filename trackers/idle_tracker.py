import time
import threading
from datetime import datetime
import logging


class IdleTracker:
    def __init__(self, event_bus, threshold=10):
        self.event_bus = event_bus
        self.threshold = threshold
        self.last_activity = time.time()
        self.idle = False
        self.total_idle_seconds = 0
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Subscribe to activity to reset the timer
        self.event_bus.subscribe("keyboard", self.activity)
        self.event_bus.subscribe("mouse_move", self.activity)
        self.event_bus.subscribe("mouse_click", self.activity)
        self.event_bus.subscribe("scroll", self.activity)

    def activity(self, event=None):
        """Reset the idle timer on any user interaction."""
        self.last_activity = time.time()
        self.idle = False

    def get_current_idle_time(self):
        """Calculates how long the user has currently been idle."""
        now = time.time()
        diff = now - self.last_activity
        return round(diff, 2) if diff > self.threshold else 0

    def _run_loop(self):
        """Background loop to check idle status every second."""
        while self.running:
            self.check_idle()
            time.sleep(1)

    def check_idle(self):
        now = time.time()
        idle_duration = now - self.last_activity

        if idle_duration > self.threshold:
            if not self.idle:
                self.idle = True
                self.event_bus.publish("idle_start", {
                    "event_type": "idle_start",
                    "timestamp": datetime.now(),
                    "metadata": {"duration_so_far": idle_duration}
                })
            # Increment total idle counter while idle
            self.total_idle_seconds += 1 
        else:
            if self.idle:
                self.idle = False
                self.event_bus.publish("idle_end", {
                    "event_type": "idle_end",
                    "timestamp": datetime.now(),
                    "metadata": {"total_idle_time": idle_duration}
                })

    def start(self):
        """Starts the idle monitoring thread."""
        if self.running:
            return
        self.running = True
        self.last_activity = time.time()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("IdleTracker thread started.")

    def stop(self):
        """Stops the idle monitoring thread."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
        self.logger.info("IdleTracker stopped.")