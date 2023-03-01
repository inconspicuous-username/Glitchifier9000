# from enum import Enum, auto
# import signal

import machine
import sys
import time

from micropython import const
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

from ctf import ctf_main
from boot import BootAnimator
from glitchifier9000 import Glitchifier9000
from graphics import OLED_WIDTH, OLED_HEIGHT, OLED_I2C_ID, OLED_I2C_SCL, OLED_I2C_SDA
from debug import print_debug
from nametag import read_namefile, write_namefile, NametagAnimator

## No enum type in micropython
# https://github.com/micropython/micropython-lib/issues/269

def enum(**enums: int):
    return type('Enum', (), enums)

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

    print_debug(f'I2C scan = {i2c.scan()}')
    print_debug(f'I2C Configuration = {i2c}')
    print_debug(f'I2C Address = 0x{i2c.scan()[0]:x}')
    
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

    return i2c, oled


class Main():
    def __init__(self, initial_state=BadgeState.BOOT) -> None:
        self.state = initial_state

        self.bootanimator = None
        self.nametaganimator = None
        self.name = ''

    def setup(self):
        self.name = read_namefile()
        self.i2c, self.oled = init_i2c_oled()

    def mainloop(self) -> None:
        self.bootanimator = BootAnimator(self.oled)
        self.nametaganimator = NametagAnimator(self.oled)

        while True:
            if self.state == BadgeState.BOOT:
                self.bootanimator.boot_animation_start(self.name,
                    boot_done_cb=lambda: self.nametaganimator.name_to_oled(self.name))

                self.state = BadgeState.IDLE
            
            elif self.state == BadgeState.MENU:
                print(menu_line())
                selected = input('> ')

                print_debug(f'{selected=}')

                try:
                    selected = int(selected)
                    if selected in BadgeState.__dict__.values():
                        self.state = selected
                    else:
                        raise ValueError
                except ValueError:
                    print(f'Invalid selection "{selected}"')
                
            elif self.state == BadgeState.NAMETAG_SHOW:
                self.name = read_namefile()
                print(f'Hello {self.name}!')

                self.nametaganimator.name_to_oled(self.name)

                self.state = BadgeState.IDLE
                
            elif self.state == BadgeState.NAMETAG_SET:
                self.oled.fill(0)
                self.oled.text('ENTER NAME OVER ', 0, 0)
                self.oled.text('USB!            ', 0, 8)
                self.oled.text('TODO MAKE BUTTON', 0, 24)
                self.oled.text('INTERFACE FOR IT', 0, 32)
                self.oled.show()

                # TODO max name length
                name = input('name?\n> ')
                if name:
                    write_namefile(name[:14])
                
                self.state = BadgeState.NAMETAG_SHOW
            
            elif self.state == BadgeState.TOGGLE_DEBUG:
                import debug
                debug.DEBUG ^= 1

                self.state = BadgeState.MENU
            
            elif self.state == BadgeState.IDLE:
                machine.idle() # Not sure this actually does anything

                # Wait for any byte over stdin
                b = sys.stdin.read(1)
                print_debug(f'{b=}')

                # Or TODO for a button press
                # self.button_handle()

                self.state = BadgeState.MENU

                # Kill any running animations
                if self.bootanimator.animating:
                    self.bootanimator.boot_animation_kill()
                if self.nametaganimator.animating:
                    self.nametaganimator.kill()
                
                
            elif self.state in [BadgeState.REPL, BadgeState.CTF, BadgeState.GLITCHIFIER9000]:
                # TODO shouldn't be neccesary to kill any animations here, but just in case
                if self.bootanimator.animating:
                    self.bootanimator.boot_animation_kill()
                if self.nametaganimator.animating:
                    self.nametaganimator.kill()

                return self.state

            else:
                self.state = BadgeState.MENU
            
    def button_handle(self, interrupts) -> None:
        print_debug('TODO: handle button press based on state')

        if interrupts & 1 == 1:
            self.state = BadgeState.MENU


if __name__ == '__main__':
    print('Riscufefe #5')
    print("Where's the FEFE, Lebowski!?")
    print()
    print('Press any button to reveal menu.')
    print()

    # m = Main(initial_state=BadgeState.GLITCHIFIER9000) # TODO: make sure it is BadgeState.BOOT (default)
    m = Main()
    m.setup()

    exit_state = m.mainloop()

    if exit_state == BadgeState.CTF:
        def link_blinker(timer):
            m.oled.fill(0)
            m.oled.text('pastebin.com/123', 0, 16)
            m.oled.text('45asdfasdfsaf   ', 0, 24)
            m.oled.show()
            time.sleep_ms(200)
            m.oled.fill(0)
            m.oled.show()
            
        m.oled.fill(0)
        m.oled.show()
        tim = Timer()
        tim.init(freq=.3, callback=link_blinker)
        ctf_main()
    if exit_state == BadgeState.GLITCHIFIER9000:
        g9k = Glitchifier9000(m.oled)
        g9k.glitchifier_loop()
    elif exit_state == BadgeState.REPL:
        # drop to interpreter, happens automatically in mpy
        pass
