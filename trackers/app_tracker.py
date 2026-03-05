import time
import win32gui
from datetime import datetime
from models.interaction_model import InteractionEvent
import logging

class AppTracker:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.running = False
        self.last_app = None
        self.logger = logging.getLogger(__name__)

    def get_active_app(self):
        try:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            return title.strip() if title else "Unknown"
        except Exception:
            return "Desktop/System"

    def run(self):
        """Main loop that polls for foreground window changes."""
        while self.running:
            try:
                current_app = self.get_active_app()

                # Only trigger event if the window actually changed
                if current_app and current_app != self.last_app:
                    event = InteractionEvent(
                        event_type="app_switch",
                        timestamp=datetime.now(),
                        metadata={"app": current_app, "previous_app": self.last_app}
                    )

                    # Update the bus with the new switch
                    self.event_bus.publish("app_switch", event)
                    self.last_app = current_app

                time.sleep(1) # Check once per second
            except Exception as e:
                self.logger.error(f"AppTracker polling error: {e}")
                time.sleep(1)

    def start(self):
        """Sets the running flag and captures the initial active app."""
        self.running = True
        # Capture current app so we don't count the first window as a 'switch'
        self.last_app = self.get_active_app()
        self.logger.info(f"AppTracker started. Initial app: {self.last_app}")

    def stop(self):
        self.running = False
        self.logger.info("AppTracker stopped.")