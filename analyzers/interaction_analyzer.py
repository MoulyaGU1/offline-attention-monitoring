import math
from collections import Counter

class InteractionAnalyzer:
    def calculate_entropy(self, events):
        """
        Measures 'Attention Entropy': Higher values indicate chaotic 
        searching; lower values indicate rhythmic flow.
        """
        if len(events) < 2:
            return 0.0

        # Extract sequence of event types
        types = [e.get('event_type') if isinstance(e, dict) else e.event_type for e in events]
        counts = Counter(types)
        total = len(types)

        # Shannon Entropy Formula
        entropy = 0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)

        return round(entropy, 4)

    def analyze(self, events):
        return {
            "entropy": self.calculate_entropy(events),
            "intensity": len(events) / 60 # Events per minute baseline
        }