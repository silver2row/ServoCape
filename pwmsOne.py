#!/usr/bin/python3

from Servo import *
from time import sleep
from flask import Flask, render_template

# create instance of ServoCtrl on i2c bus 2 at address 64 using 60hz pwm frequency.
# change 64 to 0x7f for servo cape
servos = ServoCtrl(1, 0x7f, 50)

# add a servo to controller, using channel 0.  servo max rotation is 90 degrees;
servos.add_servo("1a", 0, 90)

# add a servo to controller, using channel 15.  servo max rotation is 90 degrees;

servos.add_servo("1b", 1, 90)

servos.add_servo("2c", 3, 90)
servos.add_servo("2d", 4, 90)

servos.add_servo("3e", 6, 90)
servos.add_servo("3f", 7, 90)

servos.add_servo("4g", 9, 90)
servos.add_servo("4h", 10, 90)

servos.enablePWMs(True)

#pwm_controller.set_pwm_frequency(50)

app = Flask(__name__)
@app.route('/')
@app.route('/<state>')

def updates(state = None):
#    for l in range(0, 4):
    # Move Servo(s) to angle 2
    if state == "0":
        servos.set_servo_angle("1a", 2)
        sleep(1)
        servos.set_servo_angle("1b", 2)
        sleep(1)
        servos.set_servo_angle("2c", 2)
        sleep(1)
        servos.set_servo_angle("2d", 2)
        sleep(1)
        servos.set_servo_angle("3e", 2)
        sleep(1)
        servos.set_servo_angle("3f", 2)
        sleep(1)
        servos.set_servo_angle("4g", 2)
        sleep(1)
        servos.set_servo_angle("4h", 2)
        sleep(1)

    # servos.set_servo_angle("another servo",servos.get_servo_max_angle("another servo")/2)
    # Set the servo(s) to halfway of angle 0...
    if state == "50":
        servos.set_servo_percent("1a", 50)
        sleep(1)
        servos.set_servo_percent("1b", 50)
        sleep(1)
        servos.set_servo_percent("2c", 50)
        sleep(1)
        servos.set_servo_percent("2d", 50)
        sleep(1)
        servos.set_servo_percent("3e", 50)
        sleep(1)
        servos.set_servo_percent("3f", 50)
        sleep(1)
        servos.set_servo_percent("4g", 50)
        sleep(1)
        servos.set_servo_percent("4h", 50)
        sleep(1)

    # move servo3 to max rotation of 90 degrees
    if state == "max":
        servos.set_servo_percent("1a", 90)
        sleep(1)
        servos.set_servo_percent("1b", 90)
        sleep(1)
        servos.set_servo_percent("2c", 90)
        sleep(1)
        servos.set_servo_percent("2d", 90)
        sleep(1)
        servos.set_servo_percent("3e", 90)
        sleep(1)
        servos.set_servo_percent("3f", 90)
        sleep(1)
        servos.set_servo_percent("4g", 90)
        sleep(1)
        servos.set_servo_percent("4h", 90)
        sleep(1)

#        servos.set_servo_angle("1a", servos.get_servo_max_angle("1a"))
#        sleep(1)
#        servos.set_servo_angle("1b", servos.get_servo_max_angle("1b"))
#        sleep(1)

    # Stop everything moving for good!
    if state == "stop":
        servos.enablePWMs(False)
        sleep(1)

    template_data = {
        "title" : state,
    }
    return render_template("ServoOne.html", **template_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)