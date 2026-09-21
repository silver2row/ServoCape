from flask import Flask, render_template, request, jsonify
from macr_two import RoboticArm

app = Flask(__name__)
arm = RoboticArm()

@app.route("/")
def index():
    # Pass macro titles directly out of pre-loaded file index
    return render_template("arm_three_Flask.html", joints=arm.joints, macros=list(arm.macros.keys()))

@app.route("/api/move", methods=["POST"])
def move_joint():
    data = request.get_json() or {}
    success = arm.move_joint(data.get("joint"), data.get("angle"))
    return jsonify({"status": "success" if success else "error"})

@app.route("/api/snapshot", methods=["GET"])
def get_snapshot():
    return jsonify(arm.get_current_snapshot())

@app.route("/api/macro/save", methods=["POST"])
def save_macro():
    data = request.get_json() or {}
    name = data.get("name")
    frames = data.get("frames")
    
    if not name or not frames:
        return jsonify({"error": "Invalid name or sequence"}), 400
        
    arm.save_macro(name, frames)
    return jsonify({"status": "success", "macros": list(arm.macros.keys())})

@app.route("/api/macro/play", methods=["POST"])
def play_macro():
    data = request.get_json() or {}
    name = data.get("name")
    loop = data.get("loop", False)
    delay = float(data.get("delay", 0.6))
    
    success = arm.play_macro(name, loop=loop, speed_delay=delay)
    return jsonify({"status": "running" if success else "failed"})

@app.route("/api/macro/stop", methods=["POST"])
def stop_macro():
    arm.stop_macro()
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
