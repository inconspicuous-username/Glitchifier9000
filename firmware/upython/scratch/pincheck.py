"""
Check if the right pins are shorted together.
"""

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import utime

CROWBAR_BASE = 2
CROWBAR_COUNT = 13

PIN_LIST = list(range(29))

# Remove the GPIOs with a special function
PIN_LIST.remove(25)
PIN_LIST.remove(24)
PIN_LIST.remove(23)

# Remove the I2C display pins
PIN_LIST.remove(1)
PIN_LIST.remove(0)

# Remove the base crowbar pin
PIN_LIST.remove(CROWBAR_BASE)

# Configure the base pin as output
crowbar_base = Pin(CROWBAR_BASE, Pin.OUT, value=0)

# Configure all pins as input pull low
for p in PIN_LIST:
    Pin(p, Pin.IN, Pin.PULL_DOWN)

# Check the value of all pins
for p in PIN_LIST:
    print(f'{p} = {Pin(p).value()=}')
    assert Pin(p).value() == 0

# Set crowbar base pin to high
crowbar_base.value(1)

# Check that only the crowbar pins change to high
crowbar_list = list(range(CROWBAR_BASE, CROWBAR_BASE+CROWBAR_COUNT))
for p in PIN_LIST:
    print(f'{p} = {Pin(p).value()=}')
    if p in crowbar_list:
        assert Pin(p).value() == 1, f'Pin({p}) should be 1'
    else:
        assert Pin(p).value() == 0, f'Pin({p}) should be 0'

