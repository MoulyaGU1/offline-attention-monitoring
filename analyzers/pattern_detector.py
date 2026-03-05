from collections import Counter

class PatternDetector:
    def detect(self, events):
        """
        Detects frequency patterns of event types.
        Safely handles both dictionary and object formats.
        """
        if not events:
            return {}

        # Use a list comprehension for better performance in real-time updates
        # This handles both event.event_type (object) and event['event_type'] (dict)
        pattern_list = [
            (e.get('event_type') or e.get('type')) if isinstance(e, dict) 
            else (getattr(e, 'event_type', None) or getattr(e, 'type', 'unknown'))
            for e in events
        ]

        # Counter is already very efficient for real-time frequency mapping
        counts = Counter(pattern_list)

        return dict(counts)