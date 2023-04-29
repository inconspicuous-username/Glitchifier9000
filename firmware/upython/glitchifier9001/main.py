import struct
import sys
import time
import random

import machine

from micropython import const
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer
from rp2 import asm_pio, PIO, StateMachine

OLED_WIDTH  = 128
OLED_HEIGHT = 64
OLED_I2C_ID = 0
OLED_I2C_SDA = 0
OLED_I2C_SCL = 1

GPIO_CROWBAR_BASE = 2
GPIO_CROWBAR_COUNT = 13
GPIO_TRIGGER_IN = 15
GPIO_UART_TX = 16
GPIO_UART_RX = 17
# 18-21 are connected to buttons
GPIO_CONN_6 = 28
GPIO_CONN_7 = 29
GPIO_CONN_8 = 30

TIMEOUT_S = 2

TIME_REGEX = r"^([0-9]*)(n|u|m)?(s)?$"

# Glitcher control commands
CMD_PING = 0x30
CMD_RESET = 0x31

# Glitcher -> target commands
CMD_TARGET_RESET = 0x50

# Glitch commands
CMD_SIMPLE_GLITCH = 0x70

RET_OK = 0x00
RET_CMD_ERROR = 0x80
RET_PARAM_ERROR = 0x82
RET_GLITCH_TIMEOUT = 0x83

@asm_pio(out_init=(PIO.OUT_LOW,) * GPIO_CROWBAR_COUNT, autopull=False)
def pio_simple_glitcher():
    """
    PIO program for driving the crowbar mosfet for X amount of cycles.
    
    - NOTE: to drive all 12 pins, cannot use sideset, so will have to use regular out or set instead
    - NOTE: do not autopull with mov from osr
    - NOTE: pushing back a byte seems easier than using an irq, since it has
            to be blocking for a while anyway, could even add multiple status bytes
    """
    # Read delay and length into x and y
    pull(block)
    mov(x, osr)
    pull(block)
    mov(y, osr)

    # Last pull into osr is to use out for setting enough crowbar GPIOs
    pull(block)

    # Wait for high on trigger in
    wait(1, pin, 0)

    # TODO Add two instructions to feed back that trigger was observed via rx_fifo for visual pleasure

    label("delay_loop")
    jmp(x_dec, "delay_loop")

    # Use all 32 bits of OSR to drive 13 pins high
    out(pins, 32)
    
    label("pulse_loop")
    jmp(y_dec, "pulse_loop")

    # Clear all outpit pins to 0
    mov(pins, null)

    mov(isr, pc)
    push(block)

def crowbar_short_check():
    """
    Perform some asserts to make sure that all the mosfet driving GPIOs are actually shorted together.
    """
    PIN_LIST = list(range(29))

    # Remove the GPIOs with a special function
    PIN_LIST.remove(25)
    PIN_LIST.remove(24)
    PIN_LIST.remove(23)

    # Remove the I2C display pins
    PIN_LIST.remove(OLED_I2C_SDA)
    PIN_LIST.remove(OLED_I2C_SCL)

    # Remove the base crowbar pin
    PIN_LIST.remove(GPIO_CROWBAR_BASE)

    # Configure the base pin as output
    crowbar_base = Pin(GPIO_CROWBAR_BASE, Pin.OUT, value=0)
    crowbar_list = list(range(GPIO_CROWBAR_BASE, GPIO_CROWBAR_BASE+GPIO_CROWBAR_COUNT))

    # Configure all pins as input pull low
    for p in PIN_LIST:
        Pin(p, Pin.IN, Pin.PULL_DOWN)

    # Check the value of all pins
    pin_states = {}
    for p in PIN_LIST:
        print(f'{p} = {Pin(p).value()=}')
        pin_states[p] = Pin(p).value()
        if p in crowbar_list:
            assert Pin(p).value() == 0, f'Pin({p}) should be 0'
        else:
            # Could be 0 or 1, check that it does not go from 0 to 1 later
            pass

    # Set crowbar base pin to high
    crowbar_base.value(1)

    # Check that only the crowbar pins change to high
    for p in PIN_LIST:
        print(f'{p} = {Pin(p).value()=}')
        if p in crowbar_list:
            assert Pin(p).value() == 1, f'Pin({p}) should be 1'
        else:
            # State should not have changed
            assert Pin(p).value() == pin_states[p], f'Pin({p}) should be {pin_states[p]=}, but is {Pin(p).value()=}'
    
def rounded_unit(val, fmt='{:1.2f}'):
    if val < 1e-6:
        return fmt.format(val*1e9)  + 'n'
    if val < 1e-3:
        return fmt.format(val*1e6)  + 'u'
    if val < 1:
        return fmt.format(val*1e3)  + 'm'
    if val > 1e9:
        return fmt.format(val*1e-9) + 'M'
    if val > 1e6:
        return fmt.format(val*1e-6) + 'M'
    if val > 1e3:
        return fmt.format(val*1e-3) + 'K'
    else:
        return fmt.format(val)

class WaitAnimator():
    def __init__(self, oled):
        self.oled = oled
        self.animating = False
        self.tick0 = time.ticks_us()
        self.timer = Timer()

    def timer_cb(self, timer):
        self.oled.rect(60, 56, 68, 8, 0, True)
        # Convert to ms for more visual pleasure
        self.oled.text(f'{(time.ticks_us() - self.tick0)*1e-3:.0f}ms', 64, 56)
        self.oled.show()

    def animate(self):
        self.tick0 = time.ticks_us()
        self.timer.init(freq=20, callback=self.timer_cb)
        self.animating = True

    def kill(self):
        self.timer.deinit()
        self.animating = False

class NeedsAName():
    def __init__(self):
        self.id = None
        self.param_len = 0
        self._params = ''
    
    @property
    def params(self):
        return self._params
    
    @params.setter
    def params(self, val):
        self._params = val
        self.param_len = len(val)
    
    def bytes(self) -> bytes:
        ret = struct.pack('BH', self.id, self.param_len) + self.params
        return ret
    
    def __repr__(self) -> str:
        return f'<{self.__qualname__} @ {id(self)} [{self.id:02x} {self.param_len} {self.params}]>'


class Glitchifier9001():
    def __init__(self, verbose_serial=False, verbose_logging=False) -> None:
        """
        Class to interact with a screen if present, and a PIO for glitching.

        - verbose_serial: Enable verbose serial interaction.
        - verbose_logging: Enable verbose logging output.
        """
        self.verbose_serial = verbose_serial
        self.verbose_logging = verbose_logging
        
        self.cmd = NeedsAName()
        self.ret = NeedsAName()

        self.clock = machine.freq()
        self.delay_cycles = 200
        self.length_cycles = 500

        self.sm = StateMachine(0, pio_simple_glitcher, 
            in_base=Pin(GPIO_TRIGGER_IN, Pin.IN, Pin.PULL_DOWN), 
            out_base=Pin(GPIO_CROWBAR_BASE))
        
    def _debug(self, msg):
        print(f'[DEBUG] {msg}')
    
    def _error(self, msg):
        print(f'[ERROR] {msg}')

    def eread(self, *args):
        return sys.stdin.read(*args)
    
    def ewrite(self, *args):
        return sys.stdout.write(*args)

    def init_screen(self):
        try:
            self.i2c = I2C(OLED_I2C_ID, sda=Pin(OLED_I2C_SDA), scl=Pin(OLED_I2C_SCL))
            self.oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self.i2c)
            self.waitanimator = WaitAnimator(self.oled)
        except:
            self._error(f'Cannot instantiate screen')
            self._debug(f'I2C scan = {self.i2c.scan()}')
            self._debug(f'I2C Configuration = {self.i2c}')

        if self.oled:
            self.oled.fill(0)
            self.oled.text('GLITCHIFIER9001!', 0, 0)
            self.oled.text(f'c={rounded_unit(self.clock)}Hz', 4, 8)
            self.oled.show()

    def get_next_cmd(self) -> None:
        if self.verbose_serial:
            # TODO
            pass
        else:
            self.cmd.id, self.cmd.param_len = struct.unpack('BB', self.eread(3))
            if self.cmd.id != CMD_PING:
                self.cmd.params = self.eread(self.cmd.param_len)

    def do_cmd(self) -> None:
        if self.cmd.id == CMD_PING:
            self.ret.id = RET_OK
            self.ret.params = 'PONG'

            if self.oled:
                self.oled.text('PONG', random.randint(0, OLED_WIDTH-8*4), random.randint(0, OLED_HEIGHT-8))
                self.oled.show()

        elif self.cmd.id == CMD_RESET:
            self.ret.id = RET_OK
            self.ewrite(self.ret.bytes())
            machine.reset()

        elif self.cmd.id == CMD_SIMPLE_GLITCH:
            if self.cmd.param_len != 0:
                self.ret.id = RET_PARAM_ERROR
                self.ret.params = f'Invalid param_len={self.cmd.param_len}'
                return
            
            self.delay_cycles, self.length_cycles = struct.unpack('II', self.cmd.params)

            self.sm.active(1)
            self.sm.restart()
            self.armed = True

            if self.oled:
                # Clear area for text
                self.oled.rect(0, 8, OLED_WIDTH, OLED_HEIGHT-8, 0, True)
                self.oled.text(f'd={rounded_unit(self.delay_cycles / self.clock)}s', 4, 16)
                self.oled.text(f'l={rounded_unit(self.length_cycles / self.clock)}s', 4, 24)
                self.oled.text('ARMED!', 0, 56)
                self.oled.show()

            # Write delay and length cycle count to FIFO
            self.sm.put(self.delay_cycles)
            self.sm.put(self.length_cycles)

            # Put the value for out() instruction in OSR to drive all 13 pins high
            # DON'T PUT MORE THAN 3 VALUES INTO TX FIFO, OR IT WILL MESS WITH PUTTING PINS LOW
            # Apparently?, not sure why I wrote that -^
            pin_bits = 0b1_1111_1111_1111
            assert f'{pin_bits:b}'.count('1') == GPIO_CROWBAR_COUNT
            self.sm.put(pin_bits)

            if self.oled:
                # Start waiting for trigger animation
                self.waitanimator.animate()

            # Wait for all values to exit FIFO
            while self.sm.tx_fifo():
                pass

            # Wait for return value, or timeout
            t0 = time.time()
            while self.sm.rx_fifo() == 0:
                limit_s = (self.delay_cycles + self.length_cycles) / self.clock + TIMEOUT_S
                if time.time() - t0 > limit_s:
                    self.sm.active(0)
                    self.ret.id = RET_GLITCH_TIMEOUT
                    self.ret.params = f'Timeout after {time.time()-t0}s'

                    if self.oled:
                        self.oled.rect(0, 56, 64, 8, 0, True)
                        self.oled.text('TIMEOUT!', 0, 56)
                        self.oled.show()

                    break
            
            if self.oled:
                # Start waiting for trigger animation
                self.waitanimator.kill()

            # Nothing in rx_fifo means there was a timeout
            if self.sm.rx_fifo() != 0:
                self.ret.id = RET_OK
                self.ret.params = f'Glitch OK {self.sm.rx_fifo()}'

                if self.oled:
                    self.oled.rect(0, 56, 64, 8, 0, True)
                    self.oled.text('FIRED!', 0, 56)
                    self.oled.show()

            self.sm.active(0)
            self.armed = False

        else:
            self.ret.id = RET_CMD_ERROR
            self.ret.params = f'Invalid cmd={repr(self.cmd.id)}'
            return

    def loop(self) -> None:
        self.alive = True

        while self.alive:
            self.get_next_cmd()
            self.do_cmd()
            self.ewrite(self.ret.bytes())

        print('bye')

if __name__ == '__main__':
    print(f"GLITCHIFIER9001 - standalone version")
    print( "https://github.com/inconspicuous-username/Glitchifier9000")
    print()
    print(f"Clock speed is ~{rounded_unit(machine.freq())}Hz, or ~{rounded_unit(1/machine.freq())}s per cycle.")
    print()

    crowbar_short_check()
    g9k1 = Glitchifier9001()
    g9k1.init_screen()

    print("Entering glitcher loop, use CTRL-C to escape to REPL. Interact with g9k1 from REPL to glitch manually.")
    g9k1.loop()
    
    # # Use second core? Or scheduler?
    # import _thread
    # g9k1_id = _thread.start_new_thread(g9k1.loop)
    