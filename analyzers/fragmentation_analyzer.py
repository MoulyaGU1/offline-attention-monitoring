class FragmentationAnalyzer:
    def compute(self, events):
        """
        Calculates fragmentation based on the number of app switches.
        Works with both dictionary-based events and object-based events.
        """
        switches = 0
        
        for event in events:
            # Check if event is a dictionary
            if isinstance(event, dict):
                # Using .get() prevents KeyError if the key is missing
                if event.get("type") == "app_switch" or event.get("event_type") == "app_switch":
                    switches += 1
            # Check if event is an object
            else:
                if hasattr(event, "event_type") and event.event_type == "app_switch":
                    switches += 1
                elif hasattr(event, "type") and event.type == "app_switch":
                    switches += 1

        return switches