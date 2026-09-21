import time
from smbus2 import SMBus

class RoboticArm:
    # PCA9685 Registers
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06

    def __init__(self, bus_id=1, address=0x40, frequency=50):
        self.bus = SMBus(bus_id)
        self.address = address
        self.init_pca9685(frequency)
        
        # Configure your 4 DoF Joints: Map to PCA9685 Channels & set 'Home' angles
        self.joints = {
            "base":     {"channel": 0, "angle": 90},
            "shoulder": {"channel": 1, "angle": 90},
            "elbow":    {"channel": 2, "angle": 90},
            "gripper":  {"channel": 3, "angle": 45}
        }
        
        # Move arm to home positions on initialization
        for joint_name in self.joints:
            self.move_joint(joint_name, self.joints[joint_name]["angle"])

    def init_pca9685(self, frequency):
        """Initializes the chip and scales internal clock cycles to 50Hz."""
        self.bus.write_byte_data(self.address, self.MODE1, 0x00)
        time.sleep(0.005)
        
        prescale_val = int((25000000.0 / (4096 * frequency)) - 1.0 + 0.5)
        old_mode = self.bus.read_byte_data(self.address, self.MODE1)
        
        # Go to sleep briefly to program the frequency clock prescaler
        self.bus.write_byte_data(self.address, self.MODE1, (old_mode & 0x7F) | 0x10)
        self.bus.write_byte_data(self.address, self.PRESCALE, prescale_val)
        
        # Wake back up
        self.bus.write_byte_data(self.address, self.MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.address, self.MODE1, old_mode | 0xa1)

    def write_pwm(self, channel, on_tick, off_tick):
        """Writes low and high bits directly to I2C target registers."""
        reg_base = self.LED0_ON_L + (4 * channel)
        self.bus.write_byte_data(self.address, reg_base, on_tick & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 1, (on_tick >> 8) & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 2, off_tick & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 3, (off_tick >> 8) & 0xFF)

    def angle_to_ticks(self, angle):
        """Maps 0-180 degrees into standard 1ms - 2ms servo pulse ticks (102 to 512)."""
        min_ticks = 102
        max_ticks = 512
        return int(((angle / 180.0) * (max_ticks - min_ticks)) + min_ticks)

    def move_joint(self, joint_name, angle):
        """Updates internal dictionary and sends targeted microsecond bursts to I2C."""
        if joint_name in self.joints:
            self.joints[joint_name]["angle"] = angle
            channel = self.joints[joint_name]["channel"]
            ticks = self.angle_to_ticks(angle)
            self.write_pwm(channel, 0, ticks)
            return True
        return False
