


import random
import time
import sys
import select
import machine

from machine import Timer, Pin



class WackIt():
    def __init__(self, oled=None, buttons=None):
        self.oled = oled
        self.buttons = buttons

        self.timer = Timer()

        ### For stdin version
        # https://forum.micropython.org/viewtopic.php?t=7325
        # self.spoll = select.poll()

        self.t0 = 0
        self.t1 = int(1e6)

        self.wacked = False
        self.wacking = False

    ##### button version:
    def button_wack_handler(self, pin):
        self.timer.deinit()
        self.wacked = True

        if not self.wacking:
            print('DISHONEST WACK!!')
            if self.oled:
                self.oled.fill(0)
                self.oled.text('DISHONEST WACK!!', 0, 44)
        else:
            print(f'wackeroooo')

            self.t1 = time.ticks_us()
            self.wacking = False


            t_ms = (self.t1-self.t0) // 1000
            if self.oled:
                self.oled.fill(0)
                self.oled.text('WACK SPEED:', 0, 40)
                self.oled.text(f'{t_ms:14}ms', 0, 50)
            print(f'WACK SPEED = {t_ms:14}ms')

        bestwack_ms = None
        try:
            with open('data/bestwack.txt', 'r') as f:
                bestwack_ms = int(f.read().strip())
        except:
            print('No data/bestwack.txt found')
        if bestwack_ms:
            if self.oled:
                self.oled.text('BEST WACK:', 0, 10)
                self.oled.text(f'{bestwack_ms:14.0}ms', 0, 20)
                self.oled.show()
        if not bestwack_ms:
            bestwack_ms = t_ms
        if t_ms < bestwack_ms:
            bestwack_ms = t_ms

        if self.oled:
            self.oled.show()

        with open('data/bestwack.txt', 'w') as f:
            f.write(f'{bestwack_ms}')


    def wack(self, timer):
        print('\nWACK NOW\n')
        if self.oled:
            self.oled.fill(0)
            self.oled.text('!!!!WACK NOW!!!!', 0, 32)
            self.oled.show()
        self.wacking = True

        self.t0 = time.ticks_us()

    def start(self):
        self.wacking = False
        self.wacked = False

        self.delay_ms = random.randint(1000, 5000)
        print('STANDBY TO WACK!')
        if self.oled:
            self.oled.fill(0)
            self.oled.text('STANDBY TO WACK!', 0, 32)
            self.oled.show()
            
        # Middle button is the wack button
        self.buttons.middle.irq(self.button_wack_handler, trigger=Pin.IRQ_RISING)

        # Use a timer to start the wackening
        self.timer.init(mode=Timer.ONE_SHOT, period=self.delay_ms, callback=self.wack)

        # Wait for wacking
        while not self.wacked: pass

        self.wacking = False
        self.wacked = False
    
    def nextwack(self, pin):
        self.ready = True

    def wackloop(self):
        while True:
            self.ready = False
            self.buttons.middle.irq(self.nextwack, trigger=Pin.IRQ_RISING)
            print('push middle button to wack again')
            while not self.ready: pass
            self.start()



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
