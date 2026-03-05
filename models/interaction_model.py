from dataclasses import dataclass
from datetime import datetime


@dataclass
class InteractionEvent:
    event_type: str
    timestamp: datetime
    metadata: dict