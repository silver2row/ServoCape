import os
import json
import time
import threading
from smbus2 import SMBus

class RoboticArm:
    # PCA9685 Registers
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    
    MACRO_FILE = "macros.json"

    def __init__(self, bus_id=1, address=0x40, frequency=50):
        self.bus = SMBus(bus_id)
        self.address = address
        self.init_pca9685(frequency)
        
        self.joints = {
            "base":     {"channel": 0, "angle": 90},
            "shoulder": {"channel": 1, "angle": 90},
            "elbow":    {"channel": 2, "angle": 90},
            "gripper":  {"channel": 3, "angle": 45}
        }
        
        # Load persisted macros from file, or fall back to an empty dictionary
        self.macros = self.load_macros_from_file()
        self.is_playing = False
        self.playback_thread = None

        # Home on start
        for joint_name in self.joints:
            self.move_joint(joint_name, self.joints[joint_name]["angle"])

    def init_pca9685(self, frequency):
        self.bus.write_byte_data(self.address, self.MODE1, 0x00)
        time.sleep(0.005)
        prescale_val = int((25000000.0 / (4096 * frequency)) - 1.0 + 0.5)
        old_mode = self.bus.read_byte_data(self.address, self.MODE1)
        self.bus.write_byte_data(self.address, self.MODE1, (old_mode & 0x7F) | 0x10)
        self.bus.write_byte_data(self.address, self.PRESCALE, prescale_val)
        self.bus.write_byte_data(self.address, self.MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.address, self.MODE1, old_mode | 0xa1)

    def write_pwm(self, channel, on_tick, off_tick):
        reg_base = self.LED0_ON_L + (4 * channel)
        self.bus.write_byte_data(self.address, reg_base, on_tick & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 1, (on_tick >> 8) & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 2, off_tick & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 3, (off_tick >> 8) & 0xFF)

    def angle_to_ticks(self, angle):
        return int(((angle / 180.0) * (512 - 102)) + 102)

    def move_joint(self, joint_name, angle):
        if joint_name in self.joints:
            self.joints[joint_name]["angle"] = int(angle)
            ticks = self.angle_to_ticks(int(angle))
            self.write_pwm(self.joints[joint_name]["channel"], 0, ticks)
            return True
        return False

    def load_macros_from_file(self):
        """Reads persisted macro arrays from disk."""
        if os.path.exists(self.MACRO_FILE):
            try:
                with open(self.MACRO_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {self.MACRO_FILE}: {e}")
                return {}
        return {}

    def save_macro(self, name, frames):
        """Saves a macro locally and updates the storage file on disk."""
        self.macros[name] = frames
        try:
            with open(self.MACRO_FILE, "w") as f:
                json.dump(self.macros, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to write to {self.MACRO_FILE}: {e}")
            return False

    def get_current_snapshot(self):
        return {name: data["angle"] for name, data in self.joints.items()}

    def play_macro(self, name, loop=False, speed_delay=0.5):
        if name not in self.macros or self.is_playing:
            return False
        
        self.is_playing = True
        self.playback_thread = threading.Thread(
            target=self._macro_loop, 
            args=(name, loop, speed_delay),
            daemon=True
        )
        self.playback_thread.start()
        return True

    def stop_macro(self):
        self.is_playing = False

    def _macro_loop(self, name, loop, speed_delay):
        frames = self.macros[name]
        while self.is_playing:
            for frame in frames:
                if not self.is_playing:
                    break
                for joint_name, angle in frame.items():
                    self.move_joint(joint_name, angle)
                time.sleep(speed_delay)
            if not loop:
                break
        self.is_playing = False
