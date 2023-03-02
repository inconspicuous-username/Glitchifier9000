# https://github.com/GitJer/Some_RPI-Pico_stuff/blob/main/Button-debouncer/button_debounce.pio
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import utime

"""
.program button_debounce

    jmp pin isone   ; executed only once: is the gpio currently 0 or 1?
iszero:
    wait 1 pin 0    ; the gpio is 0, wait for it to become 1
    set x 31        ; prepare to test the gpio for 31 * 2 clock cycles
checkzero:
    ; nop [31]      ; possible location to add some pauses if longer debounce times are needed
                    ; Note: also insert a pause right after 'checkone' below

    jmp pin stillone; check if the gpio is still 1
    jmp iszero      ; if the gpio has returned to 0, start over
stillone:
    jmp x-- checkzero; the decrease the time to wait, or decide it has definitively become 1
isone:
    wait 0 pin 0    ; the gpio is 1, wait for it to become 0
    set x 31        ; prepare to test the gpio for 31 * 2 clock cycles
checkone:
    ; nop [31]      ; possible location to add some pauses if longer debounce times are needed
                    ; Note: also insert a pause right after 'checkzero' above

    jmp pin isone   ; if the gpio has returned to 1, start over
    jmp x-- checkone; decrease the time to wait
    jmp iszero      ; the gpio has definitively become 0

; the c-code must know where the border between 0 and 1 is in the code:
.define public border isone
"""

# GP20
@asm_pio()
def debounce_pio():
    jmp(pin, "isone")

    label("iszero")
    wait(1, pin, 0)
    set(x, 31)
    
    label("checkzero")
    jmp(pin, "stillone")
    jmp("iszero")

    label("stillone")
    jmp(x_dec, "checkzero")

    label("isone")
    irq(0)
    wait(0, pin, 0)
    set(x, 31)

    label("checkone")
    jmp(pin, "isone")
    jmp(x_dec, "checkone")
    jmp("iszero")

PIN_BASE = 20 # should be middle button
button_pin = Pin(PIN_BASE, Pin.IN, Pin.PULL_DOWN)


sm = StateMachine(0, debounce_pio, jmp_pin=button_pin)

def handle_button(sm):
    # TODO do it in a smarter way than restarting the state machine, statemachine seems to go weird once used irq
    sm.active(0)
    irqctx = sm.irq()
    print(f'{irqctx.flags()=}', type(sm), type(irqctx))
    sm.active(1)
    sm.restart()

sm.irq(handle_button)
sm.active(1)
