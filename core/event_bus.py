from collections import defaultdict
from threading import Lock


class EventBus:

    def __init__(self):
        self.subscribers = defaultdict(list)
        self.lock = Lock()

    def subscribe(self, event_type, callback):
        with self.lock:
            self.subscribers[event_type].append(callback)

    def publish(self, event):

        with self.lock:
            callbacks = self.subscribers.get(event.event_type, [])

        for callback in callbacks:
            callback(event)
    def publish(self, topic, data):
        print(f"DEBUG: Event fired on {topic}") # <--- ADD THIS
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                callback(data)