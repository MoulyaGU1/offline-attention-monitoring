from dataclasses import dataclass
from datetime import datetime


@dataclass
class InteractionEvent:
    def __init__(self, event_type, timestamp, app_name="Unknown", metadata=None):
        self.event_type = event_type
        self.timestamp = timestamp
        self.app_name = app_name  # Add this line
        self.metadata = metadata or {}