import os
from flask import Flask

def start_server():
    # Points to C:\...\attention-mapping-tool\dashboard
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dashboard_dir = os.path.join(base_dir, 'dashboard')

    app = Flask(__name__, 
                template_folder=dashboard_dir, 
                static_folder=dashboard_dir)

    from api.routes import register_routes
    from api.controllers import orchestrator
    
    register_routes(app, orchestrator)
    
    print(f"SERVE CHECK: Looking in {dashboard_dir}")
    app.run(host="127.0.0.1", port=5000, debug=False)