from pynput import keyboard
from datetime import datetime
from models.interaction_model import InteractionEvent
import logging


class KeyboardTracker:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.listener = None
        self.logger = logging.getLogger(__name__)

    def on_press(self, key):
        try:
            # Handle alphanumeric keys vs special keys (ctrl, alt, etc.)
            if hasattr(key, 'char') and key.char is not None:
                key_name = key.char
            else:
                key_name = str(key).replace("Key.", "")
        except Exception:
            key_name = "unknown"

        event = InteractionEvent(
            event_type="keyboard",
            timestamp=datetime.now(),
            metadata={"key": key_name}
        )

        # Ensure the topic "keyboard" matches what AttentionEngine is subscribed to
        self.event_bus.publish("keyboard", event)

    def start(self):
        if self.listener and self.listener.running:
            return

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.daemon = True  # Ensures the listener closes with the main app
        self.listener.start()
        self.logger.info("KeyboardTracker started.")

    def stop(self):
        if self.listener:
            self.listener.stop()
            try:
                self.listener.join()
            except RuntimeError:
                pass
            self.logger.info("KeyboardTracker stopped.")
    # In your KeyboardTracker
def on_press(self, key):
    try:
        key_name = key.char # normal keys
    except AttributeError:
        key_name = str(key) # special keys like Key.tab, Key.enter

    event = {
        "event_type": "keyboard",
        "key": key_name,
        "timestamp": datetime.now(),
        "app_name": self.get_active_app() 
    }
    self.event_bus.emit("keyboard", event)