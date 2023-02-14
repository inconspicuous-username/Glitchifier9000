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
bits = np.asarray(im) # TODO bytes in the framebuffer are vertical, so this should be transposed to write it directly instead of pixel by pixel

if DEBUG:
    for bitline in bits:
        for bit in bitline:
            if bit:
                print('█', end='')
            else:
                print(' ', end='')
        print()

bits = [num for elem in bits for num in elem]

if DEBUG:
    for idx, bit in enumerate(bits):
        if idx != 0 and idx % 128 == 0:
            print()
        if bit:
            print('█', end='')
        else:
            print(' ', end='')
    print()

assert len(bits) % 8 == 0

bs = bytearray([ bits[idx+0] << 7 | bits[idx+1] << 6 | bits[idx+2] << 5 | \
                 bits[idx+3] << 4 | bits[idx+4] << 3 | bits[idx+5] << 2 | \
                 bits[idx+6] << 1 | bits[idx+7] for idx in range(0, len(bits), 8)])

print(bs.hex())

bits2 = [list(f'{b:08b}') for b in bytearray(bs)]
bits2 = [num for elem in bits2 for num in elem]
bits2 = [ b == '1' for b in bits2]

if DEBUG:
    for idx, bit in enumerate(bits2):
        if idx != 0 and idx % 128 == 0:
            print()
        if bit:
            print('█', end='')
        else:
            print(' ', end='')
    print()

assert bits == bits2
