from core.session_orchestrator import SessionOrchestrator
from config import settings


# This is the "Shared Instance"
orchestrator = SessionOrchestrator()

def start_session():
    """Starts the global orchestrator session."""
    return orchestrator.start_session()

def get_session_status():
    """
    NEW: This allows your API to pull the 
    real-time 'Interaction' counts.
    """
    if not orchestrator.session_active:
        return {"status": "inactive", "message": "No session running"}
    
    # This calls the method we added to the Orchestrator earlier
    return orchestrator.get_realtime_status()
def toggle_incognito():
    settings.INCOGNITO_MODE = not settings.INCOGNITO_MODE

    if settings.INCOGNITO_MODE:
        settings.SAVE_LOGS = False
        settings.SAVE_HISTORY = False
    else:
        settings.SAVE_LOGS = True
        settings.SAVE_HISTORY = True

    return {"incognito": settings.INCOGNITO_MODE}

def end_session():
    """Ends the global session and returns the final report."""
    return orchestrator.end_session()