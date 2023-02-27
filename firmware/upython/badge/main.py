# from enum import Enum, auto
# import signal

import machine
from micropython import const
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

from ctf import ctf_main
from boot import BootAnimator
from glitchifier9000 import Glitchifier9000
from graphics import OLED_WIDTH, OLED_HEIGHT, OLED_I2C_ID, OLED_I2C_SCL, OLED_I2C_SDA

## No enum type in micropython
# https://github.com/micropython/micropython-lib/issues/269

def enum(**enums: int):
    return type('Enum', (), enums)

BadgeState = enum(
    NAMETAG_SHOW = const(1), 
    NAMETAG_SET = const(2), 
    GLITCHIFIER9000 = const(3),
    CTF = const(4),
    REPL = const(5),

    BOOT = const(90),
    MENU = const(91),

    IDLE = const(99),
)

def menu_line():
    return '\n'.join(f' {BadgeState.__dict__[x]}: {x}' for x in [
        'NAMETAG_SHOW', 
        'NAMETAG_SET', 
        'GLITCHIFIER9000', 
        'CTF',
        'REPL',
    ])

def init_i2c_oled():
    i2c = I2C(OLED_I2C_ID, sda=Pin(OLED_I2C_SDA), scl=Pin(OLED_I2C_SCL))

    print(f'[DEBUG] I2C scan = {i2c.scan()}')
    print(f'[DEBUG] I2C Configuration = {i2c}')
    print(f'[DEBUG] I2C Address = {i2c.scan()[0]:x}')
    
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

    return i2c, oled

def read_namefile():
    try: 
        with open('name.txt', 'r') as f:
            return f.read()
    except:
        return 'NONAME'

def write_namefile(name):
    with open('name.txt', 'r') as f:
        f.write(name)

def name_to_oled(oled, name):
    oled.fill(0)
    oled.text(name, 0, 0)
    oled.show()

class Main():
    def __init__(self) -> None:
        self.state = BadgeState.BOOT
        self.bootanimator = None
        self.name = ''

    def setup(self):
        self.name = read_namefile()
        self.i2c, self.oled = init_i2c_oled()

    def mainloop(self) -> None:

        print(f'Hello {self.name}!')

        while True:
            try:
                if self.state == BadgeState.BOOT:
                    self.bootanimator = BootAnimator(self.oled)
                    self.bootanimator.boot_animation_start(boot_done_cb=lambda: name_to_oled(self.oled, self.name))

                    self.state = BadgeState.MENU
                
                elif self.state == BadgeState.MENU:
                    print(menu_line())
                    selected = input('> ')

                    # Kill any running boot animation
                    if self.bootanimator:
                        self.bootanimator.boot_animation_kill()
                        self.bootanimator = None

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
                    print(f'Name: {self.name}')
                    name_to_oled(self.oled, self.name)

                    self.state = BadgeState.IDLE
                    
                elif self.state == BadgeState.NAMETAG_SET:
                    name = input('name?\n> ')
                    write_namefile(name)
                    
                    self.state = BadgeState.NAMETAG_SHOW
                
                elif self.state == BadgeState.IDLE:
                    machine.idle()

                    # print('idle out')
                
                elif self.state in [BadgeState.REPL, BadgeState.CTF, BadgeState.GLITCHIFIER9000]:
                    if self.bootanimator:
                        self.bootanimator.boot_animation_kill()
                        self.bootanimator = None

                    return self.state

                else:
                    self.state = BadgeState.MENU
            
            except KeyboardInterrupt:
                # Pretend there is a button with ctrl-c
                print('Button pressed')
                self.button_handle(0x1)

    def button_handle(self, interrupts) -> None:
        print('TODO: handle button press based on state')

        if interrupts & 1 == 1:
            self.state = BadgeState.MENU


if __name__ == '__main__':
    m = Main()
    m.setup()

    exit_state = m.mainloop()
    # exit_state = BadgeState.GLITCHIFIER9000

    if exit_state == BadgeState.CTF:
        ctf_main()
    if exit_state == BadgeState.GLITCHIFIER9000:
        glitchifier = Glitchifier9000(m.oled)
        glitchifier.glitchifier_loop()
    elif exit_state == BadgeState.REPL:
        # drop to interpreter, happens automatically in mpy
        pass
