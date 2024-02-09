from PCA96xx import *
from pathlib import Path

AUTO_INC            = (1 << 5)
SLEEP               = (1 << 4)

class Servo:
    def __init__(self, channel, max_angle):
        self.channel = channel
        self.max_angle = max_angle
        self.min_value = 0;
        self.max_value = 0;
        self.angle = 0
    def __str__(self):
        return "channel: {} max angle: {} min val: {} max val: {}".format(self.channel, self.max_angle, self.min_value, self.max_value)
    def __repr__(self):
        return "channel: {} max angle: {} min val: {} max val: {} ".format(self.channel, self.max_angle, self.min_value, self.max_value)

class ServoCtrl:
    def __init__(self, bus, addr, frequency):
        self.pwm_controller = PCA9685(bus, addr)
        self.servos = {}
        self.set_pwm_frequency(frequency)
        self.bit_time = 1.0 / (self.frequency * 4096.0)
#        set_pin = Path("/sys/class/leds/pca9685-enable/brightness")    # handling pathlib fd output instance
#        set_pin.write_text("0")


    def enablePWMs(self, en):
        set_pin = Path("/sys/class/leds/pca9685-enable/brightness")
        if en:
            set_pin.write_text("0")
        else:
            set_pin.write_text("1")

    # sets the frequency for the pwms
    def set_pwm_frequency(self, frequency):
        val = int(round(25000000 / (4096 * frequency)) - 1)
        self.frequency = frequency
        self.bit_time = 1.0/ (self.frequency * 4096.0)
        self.pwm_controller.write_reg(0, AUTO_INC | SLEEP)  ## can only set frequency in sleep mode
        self.pwm_controller.write_reg(254, val)
        self.pwm_controller.write_reg(0, AUTO_INC)

    # add a servo to the list.
    # there is no check to see if the channel has already been allocated.
    # names have to be different, but you can add multiple servos with different name
    # on the same channel
    def add_servo(self, name, servo_no, max_angle):
        assert servo_no in range(0, 16)
        self.servos[name] = Servo(servo_no, max_angle)
        self.servos[name].min_value = int(0.001 / self.bit_time)
        self.servos[name].max_value = int(0.002 / self.bit_time)


    # can be used to adjust max travel of a servo, be careful if using this
    def trim_servo(self, name, min_value, max_value):
        if name in self.servos:
            self.servos[name].min_value = min_value
            self.servos[name].max_value = max_value

    def get_servo_min_max(self, name):
        if name in self.servos:
            return [self.servos[name].min_value, self.servos[name].max_value]


    # return the max rotational angle of the servo
    def get_servo_max_angle(self, name):
        if name in self.servos:
            return self.servos[name].max_angle

    # this returns last set angle for the servo. might not actually be what the servo is at.
    def get_servo_angle(self, name):
        assert name in self.servos
        return self.servos[name].angle

    # internal function - not to be called directly.  writes out the pwm values to the chip
    def _set_servo_angle(self, servo, pwm_high):
        offset = int(servo * 200)
        pwm_start = offset
        pwm_end = int(offset + pwm_high) & 0x0fff     ## the & 0x0fff is to make sure the end is 0-4095

        on_l  = pwm_start & 0xff
        on_h  = pwm_start >> 8
        off_l = pwm_end & 0xff
        off_h = pwm_end >> 8

        values=[on_l, on_h, off_l, off_h]
        reg = 6 + (4 * servo)
        self.pwm_controller.write_regs(reg, values)


    # sets the servo based on percentage
    def set_servo_percent(self, name, percent):
        assert name in self.servos

        if percent >=0 and percent <=100:
            self.servos[name].angle = percent / 100 * self.servos[name].max_angle
            self.set_servo_angle(name, self.servos[name].angle)

    # sets the angle of the servo
    def set_servo_angle(self, name, angle):
        assert name in self.servos
        if angle >=0 and angle <= self.servos[name].max_angle:
            self.servos[name].angle=angle
            # calculate pulse time based on min & max values.
            high = self.servos[name].min_value + int((self.servos[name].max_value - self.servos[name].min_value) * self.servos[name].angle / self.servos[name].max_angle)
            self._set_servo_angle(self.servos[name].channel, high)
