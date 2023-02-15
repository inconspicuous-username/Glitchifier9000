from PIL import Image
from pprint import pprint
from binascii import b2a_base64

import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description="""Convert image to monochrome bit (1-bit) byte hexstring image for OLED display."""
)
parser.add_argument('image_file', type=str)
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('--hex', action='store_true', default=False, help='Print hex instead of base64 encoded')
args = parser.parse_args()

DEBUG = False

if args.verbose:
    DEBUG = True

im = Image.open(args.image_file)
bits = np.asarray(im) 
"""Bits in the framebuffer are organized as 

    00 08 .. 
    01 09 ..
    02 10 ..
    03 11 ..
    04 12 ..
    05 13 ..
    06 14 ..
    07 15 ..
    .  .  
    .  .

So should be transposed properly to write it directly to framebuf.buffer instead of pixel by pixel
"""

screen = ''
for bitline in bits:
    for bit in bitline:
        if bit:
            screen += '█'
        else:
            screen += ' '
    screen += '\n'
if DEBUG:
    print(screen)

bits_framebuf = np.reshape(bits.T, (128*4, 8))
bytes_framebuf = np.zeros(512, dtype=np.uint8)
for idx in range(len(bits_framebuf)):
    idx2 = (idx // 128 + idx * 4) % (128 * 4)
    byte_bits = bits_framebuf[idx2]
    byte = byte_bits[0] << 0 | byte_bits[1] << 1 | byte_bits[2] << 2 | byte_bits[3] << 3 |\
           byte_bits[4] << 4 | byte_bits[5] << 5 | byte_bits[6] << 6 | byte_bits[7] << 7
    bytes_framebuf[idx] = byte

bits2 = [list(f'{b:08b}')[::-1] for b in bytearray(bytes_framebuf)]
bits2 = [num for elem in bits2 for num in elem]
bits2 = [b == '1' for b in bits2]

screen2 = ''
for idx in range(len(bits2)):
    idx2 = (idx // 1024) * 1024 + (idx // 128) % 8 + (idx * 8) % 1024
    bit = bits2[idx2]

    if idx != 0 and idx % 128 == 0:
        screen2 += '\n'
    if bit:
        screen2 += '█'
    else:
        screen2 += ' '
screen2 += '\n'
if DEBUG:
    print(screen2)

assert bits_framebuf.shape[0]*bits_framebuf.shape[1] == 4096
assert len(bytes_framebuf) == 4096 // 8
assert screen == screen2

if args.hex:
    print(bytes(bytes_framebuf).hex())
else:
    print(b2a_base64(bytes_framebuf, newline=False).decode())
