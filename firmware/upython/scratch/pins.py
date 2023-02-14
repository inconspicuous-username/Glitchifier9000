# Drive multiple pins directly in various ways

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime

from rp2 import PIO, StateMachine, asm_pio

PIN_BASE = 6

## Via sideset can set at most 5 pins
@asm_pio(sideset_init=(PIO.OUT_LOW,) * 5)
def drive_five_side():
    nop()   .side(0b11111)

# set immediate is 5 bits, so can control at most 5 bits
@asm_pio(set_init=(PIO.OUT_LOW,) * 5)
def drive_five_set():
    set(pins, 0b11111)

## to use set with more than 5 bits (like 10 bits), need to use fifo
@asm_pio(out_init=(PIO.OUT_LOW,) * 10, autopull=True)
def drive_ten_set():
    out(pins, 32)

def side():
    sm = StateMachine(0, drive_five_side, sideset_base=Pin(PIN_BASE))
    sm.active(1)
    print(f'drive_five_side activated, {Pin(PIN_BASE)} - {Pin(PIN_BASE+4)} high')

def set5():
    sm = StateMachine(0, drive_five_set, set_base=Pin(PIN_BASE))
    sm.active(1)
    print(f'drive_five_set activated, {Pin(PIN_BASE)} - {Pin(PIN_BASE+4)} high')

def set10():
    sm = StateMachine(0, drive_ten_set, out_base=Pin(PIN_BASE))
    sm.put(0b11_1111_1111)
    sm.active(1)
    print(f'drive_ten_set activated, {Pin(PIN_BASE)} - {Pin(PIN_BASE+9)} high')

