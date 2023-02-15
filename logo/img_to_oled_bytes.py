from PIL import Image
from pprint import pprint

import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description="""Convert image to monochrome bit (1-bit) byte hexstring image for OLED display."""
)
parser.add_argument('image_file', type=str)
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

DEBUG = False

if args.verbose:
    DEBUG = True

im = Image.open(args.image_file)
bits = np.asarray(im) 
"""TODO bits in the framebuffer are organized as 

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

if DEBUG:
    for bitline in bits:
        for bit in bitline:
            if bit:
                print('█', end='')
            else:
                print(' ', end='')
        print()

bits_framebuf = np.reshape(bits.T, (128*4, 8))
for idx in range(len(bits_framebuf)):
    idx2 = (idx // 128 + idx * 4) % (128 * 4)
    byte_bits = bits_framebuf[idx2]
    byte = byte_bits[0] << 0 | byte_bits[1] << 1 | byte_bits[2] << 2 | byte_bits[3] << 3 |\
           byte_bits[4] << 4 | byte_bits[5] << 5 | byte_bits[6] << 6 | byte_bits[7] << 7
    print(f'{byte:02x}', end='')
print()

sys.exit()

bitsT = [num for elem in bits.T for num in elem]

if DEBUG:
    print()
    # Print in nested loop
    for y in range(0, 32):
        for idx in range(y, 128*32, 32):
            bit = bitsT[idx]
            # print(f'{idx:04d} ', end='')
            if bit:
                print('█', end='')
            else:
                print(' ', end='')
        print()
    print()

assert len(bitsT) % 8 == 0
assert len(bitsT) % 4096 == 0

bs = bytearray([ bitsT[idx+0] << 7 | bitsT[idx+1] << 6 | bitsT[idx+2] << 5 | \
                 bitsT[idx+3] << 4 | bitsT[idx+4] << 3 | bitsT[idx+5] << 2 | \
                 bitsT[idx+6] << 1 | bitsT[idx+7] for idx in range(0, len(bitsT), 8)])

print(bs.hex())

bits2 = [list(f'{b:08b}') for b in bytearray(bs)]
bits2 = [num for elem in bits2 for num in elem]
bits2 = [ b == '1' for b in bits2]

if DEBUG:
    # Print in single loop
    for idx in range(len(bits2)):
        idx2 = (idx // 128 + idx * 32) % (128 * 32)
        # print(f'{idx2:04d} ', end='')
        bit = bits2[idx2]
        if idx != 0 and idx % 128 == 0:
            print()
        if bit:
            print('█', end='')
        else:
            print(' ', end='')
    print()

assert bits == bits2
