import time
from flask import Flask, render_template_string, request
from smbus2 import SMBus

app = Flask(__name__)

# PCA9685 Constants
I2C_BUS = 1            # Find your bus
PCA9685_ADDRESS = 0x40 # Check address with i2cdetect -y -r 2

MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

def init_pca9685(bus, address, frequency=50):
    """Initializes the PCA9685 chip to 50Hz for servos."""
    bus.write_byte_data(address, MODE1, 0x00)
    time.sleep(0.005)
    
    # Calculate prescale value for 50Hz
    prescale_val = int((25000000.0 / (4096 * frequency)) - 1.0 + 0.5)
    
    old_mode = bus.read_byte_data(address, MODE1)
    new_mode = (old_mode & 0x7F) | 0x10  # Sleep mode to set prescale
    bus.write_byte_data(address, MODE1, new_mode)
    bus.write_byte_data(address, PRESCALE, prescale_val)
    
    bus.write_byte_data(address, MODE1, old_mode)
    time.sleep(0.005)
    bus.write_byte_data(address, MODE1, old_mode | 0xa1) 

def set_pwm(bus, address, channel, on_tick, off_tick):
    """Sets the timing registers for a specific channel."""
    reg_base = LED0_ON_L + (4 * channel)
    bus.write_byte_data(address, reg_base, on_tick & 0xFF)
    bus.write_byte_data(address, reg_base + 1, (on_tick >> 8) & 0xFF)
    bus.write_byte_data(address, reg_base + 2, off_tick & 0xFF)
    bus.write_byte_data(address, reg_base + 3, (off_tick >> 8) & 0xFF)

def angle_to_ticks(angle):
    """Maps a 0-180 degree angle to 12-bit PCA9685 ticks (approx 102 to 512)."""
    # 0 deg = ~1ms (102/4095), 180 deg = ~2ms (512/4095)
    min_ticks = 102
    max_ticks = 512
    return int(((angle / 180.0) * (max_ticks - min_ticks)) + min_ticks)

# Initialize I2C Bus & PCA9685
bus = SMBus(I2C_BUS)
init_pca9685(bus, PCA9685_ADDRESS, frequency=50)

# Track angles for 4 servos (Channels 0, 1, 2, 3). Default to 90 degrees (center).
servo_angles = {0: 90, 1: 90, 2: 90, 3: 90}

# Initialize all 4 servos to 90 degrees on startup
for ch, ang in servo_angles.items():
    set_pwm(bus, PCA9685_ADDRESS, ch, 0, angle_to_ticks(ang))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>4-Servo Control Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        .servo-container { border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 5px; max-width: 400px; }
        label { font-weight: bold; }
        .slider-group { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>PCA9685 4-Servo Control</h1>
    
    {% for ch, angle in angles.items() %}
    <div class="servo-container">
        <label>Servo Channel {{ ch }}</label>
        <form action="/set/{{ ch }}" method="POST" class="slider-group">
            <input type="range" name="angle" min="0" max="180" value="{{ angle }}" oninput="this.nextElementSibling.value = this.value + '°'">
            <output>{{ angle }}°</output>
            <input type="submit" value="Update">
        </form>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, angles=servo_angles)

@app.route("/set/<int:channel>", methods=["POST"])
def update_servo(channel):
    if channel in servo_angles:
        angle = int(request.form.get("angle", 90))
        servo_angles[channel] = angle
        
        # Turn on at 0, turn off at the calculated servo pulse width tick
        ticks = angle_to_ticks(angle)
        set_pwm(bus, PCA9685_ADDRESS, channel, 0, ticks)
        
    return index()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
