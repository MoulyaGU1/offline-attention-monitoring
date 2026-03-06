from flask import jsonify, render_template

def register_routes(app, orchestrator):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/start-session", methods=["POST"])
    def start():
        # THIS TRIGGERS THE HARDWARE LISTENERS
        return jsonify(orchestrator.start_session())

    @app.route("/status")
    def status():
        # THIS PUSHES THE DATA TO THE WEBSITE
        return jsonify(orchestrator.get_realtime_status())
    # File: api/routes.py

    @app.route("/end-session", methods=["POST"])
    def end():
    # This triggers the 'stop' command for all hardware trackers
       report = orchestrator.end_session() 
       return jsonify(report)