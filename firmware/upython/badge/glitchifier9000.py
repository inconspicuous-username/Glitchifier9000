import machine
import re
import time
import sys

from rp2 import asm_pio, PIO, StateMachine
from machine import Pin, Timer

from graphics import OLED_WIDTH, OLED_HEIGHT, dec_to_framebuf
from debug import print_debug

"""Screen layout:
128x8  (offset 0)  bits of name
128x16 (offset 8)  bits of crowbar picture
128x4  (offset 24) bits of spacer
128x8  (offset 28) space for delay setting
128x1  (offset 36) bit of spacer
128x8  (offset 37) space for length setting
128x11 (offset 45) bits of spacer
128x8  (offset 56) space for status + time elapsed

Lazily hardcoded, TODO make it less hardcoded
"""

GPIO_CROWBAR_BASE = 2
GPIO_CROWBAR_COUNT = 12
GPIO_TRIGGER_IN = 15

TIMEOUT_S = 2

TIME_REGEX = r"^([0-9]*)(n|u|m)?(s)?$"

CROWBAR = 'eJyT+/+5mZmdjY2Nj4dHRkZCwsLCwKCgICHhwYMDBw40AAEDLuBczydR4IBFghEImJmZ2dnZ2fggplpYVBQAgYWdjAQAreURRA=='
CROWBAR_WIDTH = 56
CROWBAR_HEIGHT = 16

CHARS = ['|', '/', '-', '\\']

# NOTE: to drive all 12 pins, cannot use sideset, so will have to use regular out or set instead
# NOTE: do not autopull with mov from osr
# NOTE: pushing back a byte seems easier than using an irq, since it has
#       to be blocking for a while anyway, could even add multiple status bytes
@asm_pio(out_init=(PIO.OUT_LOW,) * GPIO_CROWBAR_COUNT, autopull=False)
def simple_glitcher():
    # Read delay and length into x and y
    pull(block)
    mov(x, osr)
    pull(block)
    mov(y, osr)

    # TODO check to make sure this is equal to amount of crowbar drive pins?
    
    # Wait for high on trigger in
    wait(1, pin, 0)

    # TODO Add two instructions to feed back that trigger was observed via rx_fifo
    # Remove if you want maximum speed
    # NOTE: Maybe should be replaced with irq
    # Something like:
    ## mov(isr, pc)
    ## push(noblock)

    label("delay_loop")
    jmp(x_dec, "delay_loop")

    # TODO check if "set(pins, NUMBER)" maps 1 bit to 1 pin!
    set(pins, 12)
    
    label("pulse_loop")
    jmp(y_dec, "pulse_loop")

    set(pins, 0)

    mov(isr, pc)
    push(block)


def parse_time(time_str):
    m = re.match(TIME_REGEX, time_str)
    
    if not m:
        return None

    val, prefix, unit = m.groups()
    ret = int(val)

    if not prefix and not unit:
        print_debug(f'No unit, assuming ns')
        ret *= 1e-9
    if prefix == 'n':
        ret *= 1e-9
    elif prefix == 'u':
        ret *= 1e-6
    elif prefix == 'm':
        ret *= 1e-3
    else:
        pass

    return ret

def pretty_time(time_val):
    if time_val < 1e-6:
        return f'{time_val*1e9:5.0f}ns'
    if time_val < 1e-3:
        return f'{time_val*1e6:5.0f}us'
    if time_val < 1:
        return f'{time_val*1e3:5.0f}ms'
    else:
        return f'{time_val:5.0f}s'

# class WaitAnimator():
#     def __init__(self, oled):
#         self.oled = oled
#         self.animating = False
#         self.idx = 0
#         self.timer = Timer()
#     def timer_cb(self, timer):
#         self.oled.rect(60, 56, 8, 8, 0, True)
#         self.oled.text(CHARS[self.idx], 60, 56)
#         self.oled.show()
#         self.idx = (self.idx + 1) % len(CHARS)
#     def animate(self):
#         self.timer.init(freq=20, callback=self.timer_cb)
#         self.animating = True
#     def kill(self):
#         self.timer.deinit()
#         self.animating = True

class WaitAnimator2():
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



class Glitchifier9000():
    def __init__(self, oled=None):
        print('GLITCHIFIER9000!')
        print(f' - Configure glitch delay and glitch length as format {TIME_REGEX}.')
        print( ' - Default unit is ns.')
        print( ' - Leave empty to re-use previous values.')
        print()
        self.oled = oled
        self.delay_s = 2
        self.length_s = 2

        self.waitanimator = WaitAnimator2(oled)

    def glitchifier_loop(self):
        # TODO add a check to shift some values to make sure all pins are shorted together

        self.sm = StateMachine(0, simple_glitcher, 
            in_base=Pin(GPIO_TRIGGER_IN, Pin.IN, Pin.PULL_DOWN), 
            out_base=Pin(GPIO_CROWBAR_BASE))

        if self.oled:
            self.oled.fill(0)
            self.oled.text('GLITCHIFIER9000!', 0, 0)
            self.oled.blit(
                dec_to_framebuf(CROWBAR, CROWBAR_WIDTH, CROWBAR_HEIGHT), 
                36, 9)
            self.oled.show()

        while True:
            print(f'Glitch delay  = {pretty_time(self.delay_s)}')
            print(f'Glitch length = {pretty_time(self.length_s)}')

            while True:
                time_str = input(f'delay?\n> ')
                if not time_str:
                    break
                tmp = parse_time(time_str)
                if tmp != None:
                    self.delay_s = tmp
                    break
                print(f'Invalid input "{time_str}"')
            
            if self.oled:
                # Clear area for text
                self.oled.rect(0, 25, OLED_WIDTH, OLED_HEIGHT-25, 0, True)
                self.oled.text(f'delay:  {pretty_time(self.delay_s)}', 8, 28)
                self.oled.show()

            while True:
                time_str = input(f'length?\n> ')
                if not time_str:
                    break
                tmp = parse_time(time_str)
                if tmp != None:
                    self.length_s = tmp
                    break
                print(f'Invalid input "{time_str}"')

            if self.oled:
                self.oled.text(f'length: {pretty_time(self.length_s)}', 8, 37)
                self.oled.show()

            print_debug(f'{pretty_time(self.delay_s)=} {pretty_time(self.length_s)=}')
            print_debug(f'{machine.freq()=}')

            delay_cycles = int(self.delay_s * machine.freq())
            length_cycles = int(self.length_s * machine.freq())

            print_debug(f'{delay_cycles=}  ({pretty_time(delay_cycles * 1/machine.freq())})')
            print_debug(f'{length_cycles=} ({pretty_time(length_cycles * 1/machine.freq())})')
            
            self.sm.active(1)
            self.sm.restart()
            self.armed = True

            if self.oled:
                self.oled.rect(0, 56, 64, 8, 0, True)
                self.oled.text('ARMED!', 0, 56)
                self.oled.show()
            print('armed')

            # Write delay and length cycle count to FIFO
            self.sm.put(delay_cycles)
            print_debug(f'{self.sm.tx_fifo()=}')
            self.sm.put(length_cycles)
            print_debug(f'{self.sm.tx_fifo()=}')
            
            # Wait for all values to exit FIFO
            while self.sm.tx_fifo():
                pass
            
            # Start waiting for trigger animation
            self.waitanimator.animate()

            # Wait for return value, or timeout
            t0 = time.time()
            while self.sm.rx_fifo() == 0:
                if time.time() - t0 > (self.delay_s + self.length_s + TIMEOUT_S):
                    self.sm.active(0)
                    if self.oled:
                        self.oled.rect(0, 56, 64, 8, 0, True)
                        self.oled.text('TIMEOUT!', 0, 56)
                        self.oled.show()
                    print(f'timeout after {time.time()-t0}s')
                    break
            
            # Stop waiting for trigger animation
            self.waitanimator.kill()
            
            # Nothing in rx_fifo means there was a timeout
            if self.sm.rx_fifo():
                print_debug(f'{self.sm.rx_fifo()=}')
                if self.oled:
                    self.oled.rect(0, 56, 64, 8, 0, True)
                    self.oled.text('FIRED!', 0, 56)
                    self.oled.show()
                print(f'fired with status {self.sm.get()}')

            self.sm.active(0)
            self.armed = False
