from datetime import datetime


class Session:

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.events = []

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()

    def add_event(self, event):
        self.events.append(event)

    def duration(self):

        if not self.end_time:
            return None

        return (self.end_time - self.start_time).total_seconds()