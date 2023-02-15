# Some drawing examples

import utime
import framebuf
import _thread
import os

from zlib import decompress
from binascii import a2b_base64

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

def make_main():
    os.rename('/flash/script.py', '/main.py')

def tick(timer):
    global led
    led.toggle()

# How to do this normally??
# -> access .buffer directly, but each byte goes vertical instead of horizontal as i did now
def draw_from_horizontal_bytes(oled, bs):
    bits = [list(f'{b:08b}') for b in bs]
    bits = [num == '1' for elem in bits for num in elem]
    for idx, bit in enumerate(bits):
        oled.pixel(idx % 128, idx // 128, bit)

print('blinking LED')

led = Pin(25, Pin.OUT)
tim = Timer()

tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

print('drawing pixels')

WIDTH  = 128
HEIGHT = 32

i2c = I2C(1, sda=Pin(26), scl=Pin(27))

print(i2c.scan())
print(f'I2C Configuration: {i2c}')
print(f'I2C Address      : {i2c.scan()[0]:x}')

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

oled_x = 0
oled_y = 0

logo = b'eJy9TzFuwkAQnBwIXCBxonJBsYbCJSeKyIqQ7aec8pKDF9wLojzBD6CweAFP2IraSpUCWdnzFYAUlC4j7e3czkizCzyA2dW2Bl8mQPtJxICr66GzFb3lwdV/HA6nlZqov2kAcbHJeJcTULxu309K4Xfs5qOhbQgFZesyRVJlRKSBMtfJuMqFUVm9iCmU0CBnJn0yDVBv89GqnEqoMTKmdHqXuGTNS/Rad7BN06DTkjAwzEQWco5G/e39nS/OrotF/N4Y3JPb/gdXt3dxkd57CyuPaW1r4iW97Tz8V1jxKDU+zn4AnvtcoQ=='
logo2 = b'eJylkb0OgjAUhcEOXQz1AQi8RgcMr1Q3XLTEgbcyJAyMvkITBtYSF0xI6r0tP4oOJn5D094255576nmeVDpLJnivlfcfskTUQumQ8svj5GRMlb/cEBaHQITgJkRTPMuEflOUcpaTFuwoeBgxSgjxLcyYR+7nlksF1Lfr0K/H80ljjNkuhR0fAJeGXWYyRBxE192bpm3riaLAnp/DgW5KCEVHIzmW1gbY2egxJZgNPiNmdPND0DDipEtpELi4XHJRCKd9mh7RsxBCa6204JDOyuYTkTOHrw=='

def boot_animation(*args):
    print('drawing boot in other core')
    global oled
    oled.fill(0)
    oled.show()
    oled.vline(1, 0, HEIGHT, 1)
    oled.show()
    for _ in range(WIDTH-2):
        oled.scroll(1, 0)
        oled.show()

    oled.fill(0)
    oled.show()
    # draw_from_horizontal_bytes(oled, args[0])
    oled.buffer = decompress(a2b_base64(args[0]))
    oled.show()
    print('drawing boot done')

_thread.start_new_thread(boot_animation, (logo,))


# def oled_animate(timer):
#     global oled
    
# tim2 = Timer()
# tim2.init(freq=100, mode=Timer.PERIODIC, callback=pixelflow)

