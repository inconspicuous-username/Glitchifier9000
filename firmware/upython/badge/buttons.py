# Simpler debouncing

from machine import Pin, Timer
from micropython import const
from utils import enum

BUTTON = enum(
    LEFT   = const(18),
    DOWN   = const(19),
    MIDDLE = const(20),
    UP     = const(21),
    RIGHT  = const(22),
)

class Buttons():
    def __init__(self, oled=None):
        self.middle  = Pin(BUTTON.MIDDLE, Pin.IN, Pin.PULL_DOWN)
        self.left    = Pin(BUTTON.LEFT, Pin.IN, Pin.PULL_DOWN)
        self.up      = Pin(BUTTON.UP, Pin.IN, Pin.PULL_DOWN)
        self.right   = Pin(BUTTON.RIGHT, Pin.IN, Pin.PULL_DOWN)
        self.down    = Pin(BUTTON.DOWN, Pin.IN, Pin.PULL_DOWN)

        self.middle.irq(self.button_handler, trigger=Pin.IRQ_RISING)
        self.left.irq(self.button_handler, trigger=Pin.IRQ_RISING)
        self.up.irq(self.button_handler, trigger=Pin.IRQ_RISING)
        self.right.irq(self.button_handler, trigger=Pin.IRQ_RISING)
        self.down.irq(self.button_handler, trigger=Pin.IRQ_RISING)

        self.debouncing_delay_ms = 200 # TODO good debounce time?
        self.debouncing = False
        self.debouncing_timer = Timer()

        self.oled = oled

    def debounce_timer(self, timer):
        # print('done debouncing')
        self.debouncing = False
        
        if self.oled:
            self.oled.fill(0)
            self.oled.show()6

    def button_handler(self, pin):
        if self.debouncing:
            # print('still debouncing!')
            return

        pin_id = int(str(pin)[8:10])
        enum_idx = list(BUTTON.__dict__.values()).index(pin_id)
        button_name = list(BUTTON.__dict__.keys())[enum_idx]
        print(f'{button_name:6s} ({pin_id=}) PRESSED')

        if self.oled:
            self.oled.fill(0)
            self.oled.text(f'{button_name:6s} PRESSED', 0, 32)
            self.oled.show()

        self.debouncing = True
        self.debouncing_timer.init(mode=Timer.ONE_SHOT, period=self.debouncing_delay_ms, callback=self.debounce_timer)


    def button_state(self):
        ret = []
        ret.append(f'middle = {self.middle.value()}')
        ret.append(f'left = {self.left.value()}')
        ret.append(f'up = {self.up.value()}')
        ret.append(f'right = {self.right.value()}')
        ret.append(f'down = {self.down.value()}')
        return ret
