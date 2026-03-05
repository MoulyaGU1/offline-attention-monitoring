from analyzers.interaction_analyzer import InteractionAnalyzer

class ReportGenerator:
    def __init__(self):
        self.analyzer = InteractionAnalyzer()

    def generate(self, events):
        """
        Processes a list of events into a structured metrics dictionary.
        """
        if not events:
            return {
                "keyboard_events": 0,
                "mouse_clicks": 0,
                "mouse_moves": 0,
                "app_switches": 0
            }

        # The analyzer now handles both object and dict formats safely
        metrics = self.analyzer.analyze(events)

        # Assuming metrics is a Metrics object with a to_dict() method
        try:
            return metrics.to_dict()
        except AttributeError:
            # Fallback if to_dict() isn't implemented in your Metrics model
            return {
                "keyboard_events": metrics.keyboard_events,
                "mouse_clicks": metrics.mouse_clicks,
                "mouse_moves": metrics.mouse_moves,
                "app_switches": metrics.app_switches
            }