from PIL import Image
from pprint import pprint
from binascii import b2a_base64
from zlib import compress

import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser(description="""Convert image to monochrome bit (1-bit) byte hexstring image for OLED display.""")
parser.add_argument('image_file', type=str)
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('--no-compress', action='store_true', default=False, help='Do not compress output')
parser.add_argument('--mode', action='store', default='MONO_VLSB', help='framebuf format to use\nsee also https://docs.micropython.org/en/latest/library/framebuf.html#constants')
group = parser.add_mutually_exclusive_group()
group.add_argument('--hex', action='store_true', default=False, help='Print hex instead of base64 encoded')
group.add_argument('--raw', action='store_true', default=False, help='Print raw bytes instead of base64 encoded')
args = parser.parse_args()

DEBUG = False

if args.verbose:
    DEBUG = True

assert args.mode == 'MONO_VLSB', f'can only do --mode MONO_VLSB'

im = Image.open(args.image_file)
bits = np.asarray(im) 

if DEBUG:
    print(f'{bits.shape=}')

assert bits.shape == (32, 128) or bits.shape == (64, 128), f'cannot handle {bits.shape=}'

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

bits_framebuf = np.reshape(bits.T, (bits.shape[1] * bits.shape[0] // 8, 8))
bytes_framebuf = np.zeros(bits.shape[1] * bits.shape[0] // 8, dtype=np.uint8)
for idx in range(len(bits_framebuf)):
    idx2 = (idx // bits.shape[1] + idx * bits.shape[0] // 8) % (bits.shape[1] * bits.shape[0] // 8)
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

assert bits_framebuf.shape[0]*bits_framebuf.shape[1] in [128 * 32, 128 * 64]
assert len(bytes_framebuf) in [128 * 32 // 8, 128 * 64 // 8]
assert screen == screen2

if args.no_compress:
    compress = lambda x: x
if args.hex:
    ret = compress(bytearray(bytes_framebuf)).hex()
elif args.raw:
    ret = compress(bytearray(bytes_framebuf))
else:
    ret = b2a_base64(compress(bytes_framebuf), newline=False).decode()

print(ret)