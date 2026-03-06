from collections import defaultdict

class GravityModel:
    """
    Calculates Application 'Gravity' based on interaction density.
    Apps with high physical input 'pull' the user's attention.
    """

    def __init__(self):
        self.weights = {
            "keyboard": 1.5,    # Typing requires high active attention
            "mouse_click": 1.2, # Clicks indicate decision points
            "mouse_move": 0.5,   # Movement is lower intensity
            "scroll": 0.8       # Scrolling indicates active reading
        }

    def calculate_gravity(self, events):
        """
        Groups events by Application and calculates a 'Pull' score.
        """
        app_pull_scores = defaultdict(float)
        
        for event in events:
            # Get app name and event type safely
            app_name = event.get('app_name', 'Unknown') if isinstance(event, dict) else getattr(event, 'app_name', 'Unknown')
            event_type = event.get('event_type') if isinstance(event, dict) else getattr(event, 'event_type', None)

            if event_type in self.weights:
                app_pull_scores[app_name] += self.weights[event_type]

        # Normalize scores to percentages
        total_pull = sum(app_pull_scores.values())
        if total_pull == 0:
            return {}

        gravity_map = {
            app: round((score / total_pull) * 100, 2) 
            for app, score in app_pull_scores.items()
        }
        
        # Sort by gravity (highest pull first)
        return dict(sorted(gravity_map.items(), key=lambda item: item[1], reverse=True))