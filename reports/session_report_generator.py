import datetime

class ReportGenerator:
    def generate(self, events):
        # Helper to get values from either an Object or a Dict
        def get_val(obj, key):
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        # Count events safely
        kb = sum(1 for e in events if get_val(e, 'event_type') == 'keyboard')
        tabs = sum(1 for e in events if get_val(e, 'event_type') == 'tab_switch')
        m_clicks = sum(1 for e in events if get_val(e, 'event_type') == 'mouse_click')
        m_moves = sum(1 for e in events if get_val(e, 'event_type') == 'mouse_move')

        return {
            "keyboard": kb,
            "tab_switches": tabs,
            "mouse_clicks": m_clicks,
            "mouse_moves": m_moves,
            "total_events": len(events)
        }