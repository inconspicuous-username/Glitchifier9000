# from enum import Enum, auto
# import signal

import machine
import sys
import time

from micropython import const
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

from graphics import OLED_WIDTH, OLED_HEIGHT, OLED_I2C_ID, OLED_I2C_SCL, OLED_I2C_SDA
from buttons import Buttons
from utils import enum

BadgeState = enum(
    REPL = const(0),

    NAMETAG_SHOW = const(1), 
    GLITCHIFIER9000 = const(2),
    CTF = const(3),

    NAMETAG_SET = const(4), 
    TOGGLE_DEBUG = const(5),


    BOOT = const(90),
    MENU = const(91),

    IDLE = const(99),
)

def menu_line():
    return '\n'.join(f' {BadgeState.__dict__[x]}: {x}' for x in [
        'NAMETAG_SHOW', 
        'GLITCHIFIER9000', 
        'CTF',
    ]) + '\n\n' + '\n'.join(f' {BadgeState.__dict__[x]}: {x}' for x in [
        'NAMETAG_SET', 
        'TOGGLE_DEBUG', 
    ]) + '\n\n' + '\n'.join(f' {BadgeState.__dict__[x]}: {x}' for x in [
        'REPL',
    ])

def init_i2c_oled():
    # TODO handle non-existance of screen in I2C?

    i2c = I2C(OLED_I2C_ID, sda=Pin(OLED_I2C_SDA), scl=Pin(OLED_I2C_SCL))

    print(f'I2C scan = {i2c.scan()}')
    print(f'I2C Configuration = {i2c}')
    print(f'I2C Address = 0x{i2c.scan()[0]:x}')
    
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

    return i2c, oled


class Main():
    def __init__(self, initial_state=BadgeState.BOOT) -> None:
        pass

    def setup(self):
        self.i2c, self.oled = init_i2c_oled()
        self.buttons = Buttons(m.oled)

if __name__ == '__main__':
    print('Hello world')
    m = Main()
    m.setup()
