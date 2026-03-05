class Metrics:

    def __init__(self):
        self.keyboard_events = 0
        self.mouse_moves = 0
        self.mouse_clicks = 0
        self.app_switches = 0
        self.idle_time = 0

    def to_dict(self):

        return {
            "keyboard_events": self.keyboard_events,
            "mouse_moves": self.mouse_moves,
            "mouse_clicks": self.mouse_clicks,
            "app_switches": self.app_switches,
            "idle_time": self.idle_time
        }