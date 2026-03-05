from models.session_model import Session
from trackers.keyboard_tracker import KeyboardTracker
from trackers.mouse_tracker import MouseTracker
from trackers.app_tracker import AppTracker


class SessionManager:

    def __init__(self):

        self.session = Session()

        self.keyboard = KeyboardTracker(self.session)
        self.mouse = MouseTracker(self.session)
        self.app = AppTracker(self.session)

    def start_session(self):

        self.session.start()

        self.keyboard.start()
        self.mouse.start()

        print("Session started")

    def end_session(self):

        self.keyboard.stop()
        self.mouse.stop()
        self.app.stop()

        self.session.end()

        print("Session ended")

        return self.session.events