from models.metrics_model import Metrics

class InteractionAnalyzer:
    def analyze(self, events):
        metrics = Metrics()

        for event in events:
            # 1. Determine the event type safely (Dict vs Object)
            if isinstance(event, dict):
                e_type = event.get("event_type") or event.get("type")
            else:
                e_type = getattr(event, "event_type", None) or getattr(event, "type", None)

            # 2. Increment metrics based on the type
            if e_type == "keyboard":
                metrics.keyboard_events += 1
            elif e_type == "mouse_move":
                metrics.mouse_moves += 1
            elif e_type == "mouse_click":
                metrics.mouse_clicks += 1
            elif e_type == "app_switch":
                metrics.app_switches += 1
            elif e_type == "scroll":
                # Adding scroll support since your Orchestrator has a ScrollTracker
                metrics.mouse_moves += 1 

        return metrics