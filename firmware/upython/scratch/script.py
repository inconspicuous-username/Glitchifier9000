# Some drawing examples

import utime
import framebuf
import _thread
import os

from zlib import decompress
from binascii import a2b_base64

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

WIDTH  = 128
HEIGHT = 64

TEXT_BASE = (8, 33)

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

i2c = I2C(0, sda=Pin(0), scl=Pin(1))

print('i2c scan = ', i2c.scan())
print(f'I2C Configuration: {i2c}')
print(f'I2C Address      : {i2c.scan()[0]:x}')

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

logo_32 = b'eJy9TzFuwkAQnBwIXCBxonJBsYbCJSeKyIqQ7aec8pKDF9wLojzBD6CweAFP2IraSpUCWdnzFYAUlC4j7e3czkizCzyA2dW2Bl8mQPtJxICr66GzFb3lwdV/HA6nlZqov2kAcbHJeJcTULxu309K4Xfs5qOhbQgFZesyRVJlRKSBMtfJuMqFUVm9iCmU0CBnJn0yDVBv89GqnEqoMTKmdHqXuGTNS/Rad7BN06DTkjAwzEQWco5G/e39nS/OrotF/N4Y3JPb/gdXt3dxkd57CyuPaW1r4iW97Tz8V1jxKDU+zn4AnvtcoQ=='
logo2_32 = b'eJylkb0OgjAUhcEOXQz1AQi8RgcMr1Q3XLTEgbcyJAyMvkITBtYSF0xI6r0tP4oOJn5D094255576nmeVDpLJnivlfcfskTUQumQ8svj5GRMlb/cEBaHQITgJkRTPMuEflOUcpaTFuwoeBgxSgjxLcyYR+7nlksF1Lfr0K/H80ljjNkuhR0fAJeGXWYyRBxE192bpm3riaLAnp/DgW5KCEVHIzmW1gbY2egxJZgNPiNmdPND0DDipEtpELi4XHJRCKd9mh7RsxBCa6204JDOyuYTkTOHrw=='
logo_64 = b'eJy9UDFOwzAU/bYj20VRDVuQqqYRAyMXQIrEARBHyBF6AFANVMUTMyPdMiIOUDExcgZnY0y3IFWYHyfQgpBaJNQ32M/vv6f/vwG+QfZC2AxPZS+gtBuu02poRDmbaG0Xt1fe9/I8mXDOKT5I4Ub7AWWMQeFSVvv7o3lxKRjYqscZIUQITuZOYfC+cjHxmbQu2Or89CRJ9mL1u+YxGEzn6WEyLS6ODhJCvEYIu3HHnipFWqNSnYCCCiVCCRREw1HEmgw5wcuMKehFKnyiNYxxqZ9aHWrRFdghVH41CLphXQ84+6pbm2Ub/jpOziglG2hrkGXWfnLn/pb9Hyy7xnEUbbt7FMVxffdLWfbBSVnBMM8fACopW8axfJfnr01ALoxZ9XntvdNpnksGeturrOJd6+tmDmfMEIZ4RHbXRs0ibnBmtHnTOOIMzfRxh38AnVdy4w=='


def boot_animation(*args):
    global oled
    
    print('[core1] drawing boot in other core')

    logo = args[0]

    oled.fill(0)
    oled.blit(
        framebuf.FrameBuffer(decompress(a2b_base64(logo)), WIDTH, HEIGHT, framebuf.MONO_VLSB),
        0, 0
    )
    oled.show()

    print('[core1] drawing boot done')

_thread.start_new_thread(boot_animation, (logo_64,))

print(f'[core0] {oled=}')

# print(f'0: {id(oled.buffer)=}')
# fbuf_logo = framebuf.FrameBuffer(decompress(a2b_base64(logo_64)), WIDTH, HEIGHT, framebuf.MONO_VLSB)
# oled.blit(fbuf_logo, 0, 0)
# print(f'1: {id(oled.buffer)=}')
# print(id(oled.buffer))
# oled.show()

def write_name(oled, name):
    oled.rect(TEXT_BASE[0], TEXT_BASE[1], 8*14, 8, 0, True)
    oled.text(name[:14], TEXT_BASE[0], TEXT_BASE[1])
    oled.show()


# def oled_animate(timer):
#     global oled
    
# tim2 = Timer()
# tim2.init(freq=100, mode=Timer.PERIODIC, callback=pixelflow)

