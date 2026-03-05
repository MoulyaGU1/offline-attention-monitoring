import numpy as np

class StabilityAnalyzer:
    def compute(self, attention_timeline):
        """
        Calculates stability based on variance in the attention timeline.
        High variance = Low stability.
        """
        if not attention_timeline:
            return 0.0

        # Ensure all values are numeric and handle potential dictionary formatting
        try:
            # We filter out non-numeric values to prevent np.var from crashing
            values = [
                float(v) for v in attention_timeline.values() 
                if isinstance(v, (int, float, str)) and str(v).replace('.', '', 1).isdigit()
            ]
        except (ValueError, TypeError):
            return 0.0

        if len(values) < 2:
            return 1.0  # If there's only one data point, it's technically "stable"

        # Calculate variance
        variance = np.var(values)

        # Stability formula: 1 / (1 + variance)
        # As variance -> 0, stability -> 1
        # As variance -> infinity, stability -> 0
        stability = 1 / (1 + variance)

        return round(float(stability), 3)