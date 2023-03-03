# Simpler debouncing

from machine import Pin, Timer
from rp2 import PIO, StateMachine, asm_pio
import time
from micropython import const

def enum(**enums: int):
    return type('Enum', (), enums)

BUTTON = enum(
    LEFT   = const(18),
    DOWN   = const(19),
    MIDDLE = const(20),
    UP     = const(21),
    RIGHT  = const(22),
)

class Buttons():
    def __init__(self):
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

    def debounce_timer(self, timer):
        # print('done debouncing')
        self.debouncing = False        

    def button_handler(self, pin):
        if self.debouncing:
            # print('still debouncing!')
            return

        pin_id = int(str(pin)[8:10])
        enum_idx = list(BUTTON.__dict__.values()).index(pin_id)
        button_name = list(BUTTON.__dict__.keys())[enum_idx]
        print(f'{button_name:6s} ({pin_id=}) PRESSED')

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

buttons = Buttons() 
print('push a button see what happens')


# # https://github.com/GitJer/Some_RPI-Pico_stuff/blob/main/Button-debouncer/button_debounce.pio
# from machine import Pin
# from rp2 import PIO, StateMachine, asm_pio
# import utime

# """
# .program button_debounce

#     jmp pin isone   ; executed only once: is the gpio currently 0 or 1?
# iszero:
#     wait 1 pin 0    ; the gpio is 0, wait for it to become 1
#     set x 31        ; prepare to test the gpio for 31 * 2 clock cycles
# checkzero:
#     ; nop [31]      ; possible location to add some pauses if longer debounce times are needed
#                     ; Note: also insert a pause right after 'checkone' below

#     jmp pin stillone; check if the gpio is still 1
#     jmp iszero      ; if the gpio has returned to 0, start over
# stillone:
#     jmp x-- checkzero; the decrease the time to wait, or decide it has definitively become 1
# isone:
#     wait 0 pin 0    ; the gpio is 1, wait for it to become 0
#     set x 31        ; prepare to test the gpio for 31 * 2 clock cycles
# checkone:
#     ; nop [31]      ; possible location to add some pauses if longer debounce times are needed
#                     ; Note: also insert a pause right after 'checkzero' above

#     jmp pin isone   ; if the gpio has returned to 1, start over
#     jmp x-- checkone; decrease the time to wait
#     jmp iszero      ; the gpio has definitively become 0

# ; the c-code must know where the border between 0 and 1 is in the code:
# .define public border isone
# """

# # GP20
# @asm_pio()
# def debounce_pio():
#     jmp(pin, "isone")

#     label("iszero")
#     wait(1, pin, 0)
#     set(x, 31)
    
#     label("checkzero")
#     jmp(pin, "stillone")
#     jmp("iszero")

#     label("stillone")
#     jmp(x_dec, "checkzero")

#     label("isone")
#     irq(0)
#     wait(0, pin, 0)
#     set(x, 31)

#     label("checkone")
#     jmp(pin, "isone")
#     jmp(x_dec, "checkone")
#     jmp("iszero")

# PIN_BASE = 20 # should be middle button
# button_pin = Pin(PIN_BASE, Pin.IN, Pin.PULL_DOWN)


# sm = StateMachine(0, debounce_pio, jmp_pin=button_pin)

# def handle_button(sm):
#     # TODO do it in a smarter way than restarting the state machine, statemachine seems to go weird once used irq
#     sm.active(0)
#     irqctx = sm.irq()
#     print(f'{irqctx.flags()=}', type(sm), type(irqctx))
#     sm.active(1)
#     sm.restart()

# sm.irq(handle_button)
# sm.active(1)
