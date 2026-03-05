from pynput import mouse
from datetime import datetime
from models.interaction_model import InteractionEvent
import logging

class ScrollTracker:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.listener = None
        self.logger = logging.getLogger(__name__)

    def on_scroll(self, x, y, dx, dy):
        try:
            # Creating the event object
            event = InteractionEvent(
                event_type="scroll",
                timestamp=datetime.now(),
                metadata={
                    "x": x,
                    "y": y,
                    "dx": dx,
                    "dy": dy
                }
            )
            
            # Ensure the bus receives the event
            # If your EventBus expects a dict, use event.__dict__ 
            # or a .to_dict() method if available.
            self.event_bus.publish("scroll", event)
            
        except Exception as e:
            self.logger.error(f"Error in ScrollTracker on_scroll: {e}")

    def start(self):
        if self.listener and self.listener.running:
            return
            
        self.listener = mouse.Listener(
            on_scroll=self.on_scroll
        )
        # We use daemon=True so the listener dies if the main thread dies
        self.listener.daemon = True
        self.listener.start()
        self.logger.info("ScrollTracker started.")

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener.join() # Wait for thread to clean up
            self.logger.info("ScrollTracker stopped.")