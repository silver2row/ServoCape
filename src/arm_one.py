import time
from flask import Flask, render_template_string, request, jsonify
from smbus2 import SMBus

app = Flask(__name__)

# PCA9685 Config
I2C_BUS = 1            
PCA9685_ADDRESS = 0x40  

MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

def init_pca9685(bus, address, frequency=50):
    bus.write_byte_data(address, MODE1, 0x00)
    time.sleep(0.005)
    prescale_val = int((25000000.0 / (4096 * frequency)) - 1.0 + 0.5)
    
    old_mode = bus.read_byte_data(address, MODE1)
    new_mode = (old_mode & 0x7F) | 0x10  
    bus.write_byte_data(address, MODE1, new_mode)
    bus.write_byte_data(address, PRESCALE, prescale_val)
    
    bus.write_byte_data(address, MODE1, old_mode)
    time.sleep(0.005)
    bus.write_byte_data(address, MODE1, old_mode | 0xa1) 

def set_pwm(bus, address, channel, on_tick, off_tick):
    reg_base = LED0_ON_L + (4 * channel)
    bus.write_byte_data(address, reg_base, on_tick & 0xFF)
    bus.write_byte_data(address, reg_base + 1, (on_tick >> 8) & 0xFF)
    bus.write_byte_data(address, reg_base + 2, off_tick & 0xFF)
    bus.write_byte_data(address, reg_base + 3, (off_tick >> 8) & 0xFF)

def angle_to_ticks(angle):
    # Standard 1ms to 2ms mapping (102 to 512 ticks) [3]
    min_ticks = 102
    max_ticks = 512
    return int(((angle / 180.0) * (max_ticks - min_ticks)) + min_ticks)

# Initialize I2C Bus & PCA9685
bus = SMBus(I2C_BUS)
init_pca9685(bus, PCA9685_ADDRESS, frequency=50)

# Map 4 DoF Joints to PCA9685 Channels and starting angles
arm_joints = {
    "base":     {"channel": 0, "angle": 90},
    "shoulder": {"channel": 1, "angle": 90},
    "elbow":    {"channel": 2, "angle": 90},
    "gripper":  {"channel": 3, "angle": 45}  # Often starts open/half-way
}

# Move arm to home position on startup
for joint, data in arm_joints.items():
    set_pwm(bus, PCA9685_ADDRESS, data["channel"], 0, angle_to_ticks(data["angle"]))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>4 DoF Robotic Arm Controller</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f4f6f9; color: #333; }
        .dashboard { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; font-size: 24px; margin-bottom: 30px; }
        .joint-control { margin-bottom: 25px; }
        .joint-header { display: flex; justify-content: space-between; font-weight: bold; text-transform: capitalize; color: #34495e; }
        input[type=range] { width: 100%; margin-top: 10px; height: 8px; border-radius: 5px; background: #ddd; accent-color: #3498db; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>4 DoF Robotic Arm Control</h1>
        
        {% for joint, data in joints.items() %}
        <div class="joint-control">
            <div class="joint-header">
                <span>{{ joint }} (CH {{ data.channel }})</span>
                <span id="{{ joint }}-val">{{ data.angle }}°</span>
            </div>
            <input type="range" min="0" max="180" value="{{ data.angle }}" 
                   oninput="updateJoint('{{ joint }}', this.value)">
        </div>
        {% endfor %}
    </div>

    <script>
        function updateJoint(jointName, angle) {
            // Update the browser text instantly
            document.getElementById(jointName + '-val').innerText = angle + '°';
            
            // Send the new angle to Flask in the background
            fetch('/set_joint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `joint=${jointName}&angle=${angle}`
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, joints=arm_joints)

@app.route("/set_joint", methods=["POST"])
def set_joint():
    joint = request.form.get("joint")
    angle = int(request.form.get("angle", 90))
    
    if joint in arm_joints:
        arm_joints[joint]["angle"] = angle
        channel = arm_joints[joint]["channel"]
        
        # Write to I2C register
        ticks = angle_to_ticks(angle)
        set_pwm(bus, PCA9685_ADDRESS, channel, 0, ticks)
        return jsonify({"status": "success", "joint": joint, "angle": angle})
        
    return jsonify({"status": "error", "message": "Invalid joint"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
