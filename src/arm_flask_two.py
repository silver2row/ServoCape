from flask import Flask, render_template, request, jsonify
from arm_two import RoboticArm

app = Flask(__name__)

# Initialize our physical 4 DoF robotic arm hardware object
arm = RoboticArm(bus_id=1, address=0x40, frequency=50)

@app.route("/")
def index():
    # Pass current joint angles so the HTML sliders load on their correct positions
    return render_template("index.html", joints=arm.joints)

@app.route("/api/move", methods=["POST"])
def move_joint():
    # Expects JSON data payload from the frontend JavaScript engine
    data = request.get_json() or {}
    joint = data.get("joint")
    angle = data.get("angle")
    
    if joint is None or angle is None:
        return jsonify({"error": "Missing joint or angle parameters"}), 400
        
    try:
        angle = int(angle)
    except ValueError:
        return jsonify({"error": "Angle must be a number"}), 400

    # Command physical arm to turn I2C registers
    success = arm.move_joint(joint, angle)
    
    if success:
        return jsonify({"status": "success", "joint": joint, "angle": angle})
    return jsonify({"error": "Target joint not found"}), 404

if __name__ == "__main__":
    # Host on 0.0.0.0 allows any laptop or phone on your WiFi to control the arm
    app.run(host="0.0.0.0", port=5000, debug=True)
