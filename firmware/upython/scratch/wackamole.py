


import random
import time
import sys
import select

from machine import Timer


class WackIt():
    def __init__(self, oled=None):
        self.timer = Timer()

        # Add a poll thingy to catch cheaters
        # https://forum.micropython.org/viewtopic.php?t=7325

        self.spoll = select.poll()
        self.wacked = False

    def wack(self, timer):
        print('\nWACK NOW\n')
        t0 = time.ticks_us()
        y = sys.stdin.read(1)
        t1 = time.ticks_us()
        # print(t0, t1, t1-t0)
        print(f'WACK SPEED = {t1-t0}us')

        self.wacked = True


    def start(self):
        self.spoll.register(sys.stdin, select.POLLIN)
        self.wacked = False
        self.delay_ms = random.randint(50, 5000)
        self.timer.init(mode=Timer.ONE_SHOT, period=self.delay_ms, callback=self.wack)

        print('READY TO WACK')
        while not self.wacked: 
            x = sys.stdin.read(1) if self.spoll.poll(0) else None
            if x:
                self.timer.deinit()
                # print(f'{repr(x)=}, {self.wacked=}')
                print('DISHONEST WACK')
                break

        self.spoll.unregister(sys.stdin)


w = WackIt()

# from wackamole import *