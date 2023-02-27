import machine
import rp2

@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def pin_toggle():
    set(pins, 3)
    set(pins, 0)

def toggle():
    print(f'{machine.freq()=}')
    machine.freq(int(266e6))
    print(f'{machine.freq()=}')
    sm = rp2.StateMachine(0, pin_toggle, set_base=machine.Pin(25))
    sm.active(1)
    print(f'{sm.active()=}')
    return sm

sm = toggle()