# Simpler debouncing

from machine import Pin, Timer
from micropython import const

from utils import enum
from debug import print_debug

BUTTON = enum(
    LEFT   = const(18),
    DOWN   = const(19),
    MIDDLE = const(20),
    UP     = const(21),
    RIGHT  = const(22),
)

def button_info(pin):
    pin_id = int(str(pin)[8:10])
    enum_idx = list(BUTTON.__dict__.values()).index(pin_id)
    button_name = list(BUTTON.__dict__.keys())[enum_idx]
    return(pin_id, enum_idx, button_name)

class Buttons():
    def __init__(self, oled=None):
        self.middle  = Pin(BUTTON.MIDDLE, Pin.IN, Pin.PULL_DOWN)
        self.left    = Pin(BUTTON.LEFT,   Pin.IN, Pin.PULL_DOWN)
        self.up      = Pin(BUTTON.UP,     Pin.IN, Pin.PULL_DOWN)
        self.right   = Pin(BUTTON.RIGHT,  Pin.IN, Pin.PULL_DOWN)
        self.down    = Pin(BUTTON.DOWN,   Pin.IN, Pin.PULL_DOWN)

        self.middle.irq(self.button_handler, trigger=Pin.IRQ_RISING)
        self.left.irq(  self.button_handler, trigger=Pin.IRQ_RISING)
        self.up.irq(    self.button_handler, trigger=Pin.IRQ_RISING)
        self.right.irq( self.button_handler, trigger=Pin.IRQ_RISING)
        self.down.irq(  self.button_handler, trigger=Pin.IRQ_RISING)

        self.debouncing_delay_ms = 150 # TODO good debounce time?
        self.debouncing = False
        self.debouncing_timer = Timer()

        self.recent = None

        self.oled = oled

        self.button_action = self.button_debug_print

    def debounce_timer(self, timer):
        # print('done debouncing')
        self.debouncing = False
        
    def button_handler(self, pin):
        if self.debouncing:
            return

        # If not debouncing, start debouncing and trigger button action
        self.debouncing = True
        self.debouncing_timer.init(mode=Timer.ONE_SHOT, period=self.debouncing_delay_ms, callback=self.debounce_timer)
        
        if self.button_action:
            print_debug(f'{pin=} button_action')
            self.button_action(pin)
    
    def button_raise_exception(self, pin):
        raise Exception(button_info(pin))

    def button_record_recent(self, pin):
        # Record most recently seen button
        self.recent = button_info(pin)

    def button_debug_print(self, pin):
        pin_id, enum_idx, button_name = button_info(pin)
        print(f'{button_name:6s} ({pin_id=}) PRESSED')

        if self.oled:
            self.oled.fill(0)
            self.oled.text(f'{button_name:6s} PRESSED', 0, 32)
            self.oled.show()

    def button_state(self):
        ret = []
        ret.append(f'middle = {self.middle.value()}')
        ret.append(f'left = {self.left.value()}')
        ret.append(f'up = {self.up.value()}')
        ret.append(f'right = {self.right.value()}')
        ret.append(f'down = {self.down.value()}')
        return ret
