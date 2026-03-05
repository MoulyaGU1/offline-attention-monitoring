from statistics import mean, variance, StatisticsError

class MetricsUtils:
    @staticmethod
    def interaction_rate(events, duration):
        """Calculates events per second."""
        if not events or duration <= 0:
            return 0.0
        return round(len(events) / duration, 2)

    @staticmethod
    def calculate_variance(values):
        """Calculates variance safely for real-time data streams."""
        # Filter for actual numbers to prevent StatisticsError
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        if len(numeric_values) < 2:
            return 0.0
        
        try:
            return variance(numeric_values)
        except StatisticsError:
            return 0.0

    @staticmethod
    def average(values):
        """Calculates mean safely."""
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        if not numeric_values:
            return 0.0
            
        try:
            return mean(numeric_values)
        except StatisticsError:
            return 0.0

    @staticmethod
    def normalize(value, max_value):
        """Normalizes a value between 0 and 1."""
        if max_value <= 0:
            return 0.0
        
        result = value / max_value
        return min(max(result, 0.0), 1.0) # Clamp between 0 and 1