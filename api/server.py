from flask import Flask
import os

def start_server():
    # Get the absolute path to the 'dashboard' folder
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dashboard'))
    
    app = Flask(__name__, 
                static_folder=base_dir,       # Flask will look here for /static/
                template_folder=base_dir)     # Flask will look here for render_template()

    from api.routes import register_routes
    from api.controllers import orchestrator
    register_routes(app, orchestrator)

    app.run(host="127.0.0.1", port=5000, debug=False)