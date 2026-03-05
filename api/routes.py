from flask import render_template, jsonify

def register_routes(app, orchestrator):
    @app.route("/")
    def index():
        # Ensure there is NO "Attention Mapping Backend Running" string here
        return render_template("index.html")

    @app.route("/status")
    def status():
        return jsonify(orchestrator.get_realtime_status())
    
    # ... start/end routes ...