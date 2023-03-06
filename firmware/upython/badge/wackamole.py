


import random
import time
import sys
import select

from machine import Timer


class WackIt():
    def __init__(self, oled=None, buttons=None):
        self.oled = oled
        self.buttons = buttons

        self.timer = Timer()

        # Use a poll to catch cheaters
        # https://forum.micropython.org/viewtopic.php?t=7325

        self.spoll = select.poll()
        self.wacked = False

    ##### button version:
    def wack(self, timer):
        print('\nWACK NOW\n')
        if self.oled:
            self.oled.fill(0)
            self.oled.text('!!!!WACK NOW!!!!', 0, 32)
            self.oled.show()
        self.wacking = True
        t0 = time.ticks_us()
        while not self.buttons.recent: pass
        t1 = time.ticks_us()
        self.wacking = False
        if self.oled:
            self.oled.fill(0)
            self.oled.text('WACK SPEED:', 0, 32)
            self.oled.text(f'{t1-t0:14}us', 0, 42)
            self.oled.show()
        print(f'WACK SPEED = {t1-t0}us')
        self.wacked = True

    def start(self):
        self.buttons.recent = None
        self.wacked = False
        self.delay_ms = random.randint(1000, 5000)
        print('STANDBY TO WACK!')
        if self.oled:
            self.oled.fill(0)
            self.oled.text('STANDBY TO WACK!', 0, 32)
            self.oled.show()
        self.timer.init(mode=Timer.ONE_SHOT, period=self.delay_ms, callback=self.wack)

        while not self.wacking:
            if self.buttons.recent:
                self.timer.deinit()
                print('DISHONEST WACK!!')
                if self.oled:
                    self.oled.fill(0)
                    self.oled.text('DISHONEST WACK!!', 0, 32)
                    self.oled.show()

        # Wait for the wack
        while not self.wacked: pass
        self.wacking = False
        self.wacked = False

        time.sleep(1)

    ##### stdin version
    # def wack(self, timer):
    #     print('\nWACK NOW\n')
    #     t0 = time.ticks_us()
    #     y = sys.stdin.read(1)
    #     t1 = time.ticks_us()
    #     # print(t0, t1, t1-t0)
    #     print(f'WACK SPEED = {t1-t0}us')
    #     self.wacked = True
    # def start(self):
    #     self.spoll.register(sys.stdin, select.POLLIN)
    #     self.wacked = False
    #     self.delay_ms = random.randint(1000, 5000)
    #     print('READY TO WACK')
    #     self.timer.init(mode=Timer.ONE_SHOT, period=self.delay_ms, callback=self.wack)
    #     while not self.wacked: 
    #         x = sys.stdin.read(1) if self.spoll.poll(0) else None
    #         if x:
    #             self.timer.deinit()
    #             # print(f'{repr(x)=}, {self.wacked=}')
    #             print('DISHONEST WACK')
    #             break
    #     self.spoll.unregister(sys.stdin)
