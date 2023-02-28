import machine
import re
import time

from rp2 import asm_pio, PIO, StateMachine
from machine import Pin

from graphics import OLED_WIDTH, OLED_HEIGHT
from debug import print_debug

GPIO_CROWBAR_BASE = 2
GPIO_CROWBAR_COUNT = 12
GPIO_TRIGGER_IN = 15

TIMEOUT_S = 1

# NOTE: to drive all 12 pins, cannot use sideset, so will have to use regular out or set instead
# NOTE: do not autopull with mov from osr
@asm_pio(out_init=(PIO.OUT_LOW,) * GPIO_CROWBAR_COUNT, autopull=False)
def simple_glitcher():
    # Read delay and length into x and y
    pull(block)
    mov(x, osr)
    pull(block)
    mov(y, osr)

    # TODO check to make sure this is equal to amount of crowbar drive pins?
    # Put amount of driver pins into OSR
    pull(block)
    
    # Clear done IRQ
    irq(clear, 0)

    # Wait for high on trigger in
    # wait(1, pin, 15)

    label("delay_loop")
    jmp(x_dec, "delay_loop")

    # TODO check if "set(pins, NUMBER)" maps 1 bit to 1 pin!
    set(pins, 12)
    
    label("pulse_loop")
    jmp(y_dec, "pulse_loop")

    irq(0)






TIME_REGEX = regex = r"^([0-9]*)(n|u|m)?(s)?$"

def parse_time(time_str):
    m = re.match(TIME_REGEX, time_str)
    
    if not m:
        return None

    val, prefix, unit = m.groups()
    ret = int(val)

    if not unit:
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
        return f'{time_val:5.0}s'

class Glitchifier9000():
    def __init__(self, oled=None):
        print('GLITCHIFIER9000')

        self.oled = oled
        self.delay_s = 0
        self.length_s = 0

    def glitch_done_handler(self, irq):
        self.armed = False
        self.sm.active(0)
        
        if self.oled:
            self.oled.text('FIRED!', 8*8, 7*8)
            self.oled.show()
        print('FIRED!')

    def glitchifier_loop(self):

        # TODO add a check to shift some values to make sure all pins are shorted together

        self.sm = StateMachine(0, simple_glitcher, in_base=Pin(GPIO_TRIGGER_IN), out_base=Pin(GPIO_CROWBAR_BASE))
        self.sm.active(0)

        self.sm.irq(self.glitch_done_handler)

        if self.oled:
            self.oled.fill(0)
            self.oled.text('GLITCHIFIER9000!', 0*8, 0*8)
            self.oled.show()

        while True:
            if self.oled:
                self.oled.rect(0, 8, OLED_WIDTH, OLED_HEIGHT-8, 0, True)

            while True:
                time_str = input(f'delay  [{pretty_time(self.delay_s)}] ? > ')
                if not time_str:
                    break
                tmp = parse_time(time_str)
                if tmp:
                    self.delay_s = tmp
                    break
            
            if self.oled:
                self.oled.text(f'delay:  {pretty_time(self.delay_s)}', 1*8, 2*8)
                self.oled.show()

            while True:
                time_str = input(f'length [{pretty_time(self.length_s)}] ? > ')
                if not time_str:
                    break
                tmp = parse_time(time_str)
                if tmp:
                    self.length_s = tmp
                    break

            if self.oled:
                self.oled.text(f'length: {pretty_time(self.length_s)}', 1*8, int(3.5*8))
                self.oled.show()

            print_debug(f'{pretty_time(self.delay_s)=} {pretty_time(self.length_s)=}')
            print_debug(f'{machine.freq()=}')

            delay_cycles = int(self.delay_s * machine.freq())
            length_cycles = int(self.length_s * machine.freq())

            print_debug(f'{delay_cycles=}  ({pretty_time(delay_cycles * 1/machine.freq())})')
            print_debug(f'{length_cycles=} ({pretty_time(length_cycles * 1/machine.freq())})')
            
            self.sm.active(1)
            self.armed = True

            if self.oled:
                self.oled.text('ARMED!', 0*8, 7*8)
                self.oled.show()
            print('ARMED!')

            # Write delay and length cycle count to FIFO
            self.sm.put(delay_cycles)
            print(f'{self.sm.tx_fifo()=}')
            self.sm.put(length_cycles)
            print(f'{self.sm.tx_fifo()=}')
            

            # Wait for all values to visit FIFO
            while self.sm.tx_fifo():
                pass

            # Wait for interrupt handler to be triggered and done
            t0 = time.time()
            while self.armed:
                if time.time() - t0 > TIMEOUT_S:
                    if self.oled:
                        self.oled.text('TIMEOUT!', 8*8, 7*8)
                        self.oled.show()
                    print(f'timeout after {time.time()-t0}')
                    break
            
            self.armed = False
            self.sm.active(0)