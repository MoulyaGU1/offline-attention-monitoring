from pynput import mouse
from datetime import datetime
from models.interaction_model import InteractionEvent
import time


class MouseTracker:

    def __init__(self, event_bus):

        self.event_bus = event_bus
        self.listener = None
        self.last_move_time = 0

    def on_move(self, x, y):
        # Create a simple data packet for the event bus
        event = {
            "event_type": "mouse_move",
            "x": x,
            "y": y,
            "timestamp": datetime.now() # Fixed: removed the double '.datetime'
        }
        self.event_bus.publish("mouse_move", event)
        
    def on_click(self, x, y, button, pressed):

        if pressed:

            event = InteractionEvent(
                event_type="mouse_click",
                timestamp=datetime.now(),
                metadata={"button": str(button)}
            )

            self.event_bus.publish("mouse_click", event)

    def start(self):

        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )

        self.listener.start()

    def stop(self):

        if self.listener:
            self.listener.stop()
    