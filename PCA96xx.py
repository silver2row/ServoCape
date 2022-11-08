from smbus2 import SMBus
from time import sleep

# registers!

Mode1               = 0x00
Mode2               = 0x01
LED                 = 0x06
All_LED             = 0xFA
PRE_SCALE           = 0xFE
DEFAULT_FREQUENCY   = 200
AUTO_INC            = (1 << 5)
SLEEP               = (1 << 4)

class PCA9685:
  def __init__(self, bus, addr):
    self.addr = addr
    self.bus = SMBus(bus)
    self.write_reg(Mode1, AUTO_INC)
    sleep(500e-6)

  def read_reg(self, reg):
    assert reg in range(0, 256)
    return self.read_regs(reg, 1)[0]

  def write_reg(self, reg, value):
    return self.write_regs(reg, [value])

  def read_regs(self, reg, value):
    assert reg in range(0, 256)
    assert value in range(1, 257 - reg)
    return self.bus.read_i2c_block_data(self.addr, reg, value)

  def write_regs(self, reg, values):
    assert reg in range(0, 256)
    return self.bus.write_i2c_block_data(self.addr, reg, values)

  def get_pwm(self, output):
    assert output in range(0, 16)
    reg = LED + 4 * output

    [on_l, on_h, off_l, off_h] = self.read_regs(reg, 4)
    on  = on_l | on_h << 8
    off = off_l | off_h << 8

    phase = on
    duty = (off - on) & 0xfff
    if off & 0x1000:
      duty = 0
    elif on & 0x1000:
      duty = 4096
    return (duty, phase)

  def set_pwm(self, output, duty, phase = 0):
    assert duty in range(0, 4097)
    assert phase in range(0, 4096)

    if output == "all":
      reg = All_LED
    else:
      assert output in range(0, 16)
      reg = LED +4 * output

    on  = phase
    off = (duty + phase) & 0xfff
    if duty == 0:
      off |= 0x1000
    elif duty == 4096:
      on |= 0x1000

    on_l  = on & 0xff
    on_h  = on >> 8
    off_l = off & 0xff
    off_h = off >> 8
    self.write_regs(reg, [on_l, on_h, off_l, off_h])