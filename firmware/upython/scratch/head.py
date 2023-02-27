import utime
import framebuf
import _thread
import os
import uasyncio

from zlib import decompress
from binascii import a2b_base64

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

def make_main():
    os.rename('/flash/head.py', '/main.py')

HEAD = [
    # Closed
    'eJxtkL1OwzAQx8+xVXvqMWZAuEysGRFD8wi8QphYeQBE3CfoI/AqZupYRkaLAUY8erBSLo4TVU1+sk/2/e372t7sj493WgI458MZPuGIDeEm/CRYYHylrqqnHZes4wwSFbD2tECNQqz0knJqQZbeWgOsAA5nMC4RUWcQ5ZgEQJK7HhnEpN0e9PNeP3w2TVOVShRwiaFlLGVL1jmTuHhj/RtCcoovB4DbGNwoeh+795SQIIsZulB79/mVC9dryT98KYpUF2OglBJjA8Z11Pjf77cFKHq6xLqggs2GNJXjoK56W9tZI4NcT8PuQvQ/4zl62v3pNYaXZvnvLBaV3/bhWhpp3r2n1ajlfJAD/3x+yS4=',
    # Open
    'eJxtkKtSxDAUhk+azCaKg6xgyKKwlQxi8wi8QlFYHoDZdFVlH4FXCWrlIpEZBEgiKzIpaXqZnW2/SY44f/Kfy+62OT3dSw5grWvPcAkb2UbsjJsFA4RuxHXxfKCcBEogUQDR3QoKGdvINaXTwHNnTAUkAwpnEMoRUY4g8qkIAI9pNTGISbs7ypdGPn6WZVnkgmVwSRVPZWK1FK2tEhdvjNsjpCT7sgC4862dROd8eJeyOR1rHtvrO0zUNcbxHsZXtr254vTD5SxLfRECQgg2DVDZEAf/+/02hKPSeh8GtJL8sI2aGH1QFn1UZjHIIKt52aH17me0Cd51wffZN9++lut/F16xfd3b6bjS8fYZLVHy5SIH/gGLBtBA',
]
HEAD_WIDTH = 72
HEAD_HEIGHT = 64

# Toggle mouth, no need to clear every draw, draw over it with blit
# TODO: could optimize by only drawing the mouth? probably most of the overhead is sending the updated framebuf, so probably won't matter
head_state = 0
def mouth_toggle(timer=None):
    global oled
    global head_state
    oled.blit(framebuf.FrameBuffer(decompress(a2b_base64(HEAD[head_state])), HEAD_WIDTH, HEAD_HEIGHT, framebuf.MONO_VLSB), 0, 0)
    oled.show()
    head_state ^= 1
mouth_timer = Timer()

WIDTH  = 128
HEIGHT = 64

TEXT_BASE = HEAD_WIDTH
LINE_SIZE = WIDTH - TEXT_BASE
LINE_CHARS = LINE_SIZE // 8
TEXT_SPACE = LINE_SIZE // 8 * (HEIGHT // 8)

I2C_ID = 0
I2C_SDA = 0
I2C_SCL = 1

NAME = 'TODONAME14CHAR'

WELCOME_MESSAGE = (
    "{:<14}"
    "       "
    "-------"
    "       "
    "On be- "
    "half of"
    "the Or-"
    "gani-  "
    "zers of"
    "the    "
    "Riscure"
    "Federa-"
    "tion of"
    "Enter- "
    "tainers"
    "and    "
    "Funny  "
    "Endea- "
    "vors,  "
    "welcome"
    "to the "
    "fifth  "
    "volume "
    "of     "
    "riscu- "
    "fefe!  ")

print('[core0] init oled')
i2c = I2C(I2C_ID, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# for idx in range(0, len(WELCOME_MESSAGE), LINE_CHARS): 
#     print(WELCOME_MESSAGE[idx:idx+LINE_CHARS].decode())

# for idx in range(0, LINE_CHARS * (HEIGHT // 8), LINE_CHARS): 
#     oled.text(WELCOME_MESSAGE[idx:idx+LINE_CHARS], TEXT_BASE, idx // LINE_CHARS * (HEIGHT // 8)); 
#     oled.show(); 
#     utime.sleep_ms(500)

# for idx in range(-1 * (LINE_CHARS*HEIGHT//8) + LINE_CHARS, len(WELCOME_MESSAGE), LINE_CHARS):
#     start = max(idx, 0)
#     end = idx+(LINE_CHARS*HEIGHT//8)
#     # print(start,end)
#     visible = WELCOME_MESSAGE[start:end]
#     for idx2 in range(0, LINE_CHARS*HEIGHT//8, LINE_CHARS): 
#         print(visible[idx2:idx2+LINE_CHARS].decode())
#     print('-'*LINE_CHARS)

# def scrolling_welcome(name):
#     global oled

#     name = name[:14]
#     message = WELCOME_MESSAGE.format(name)

#     # Draw scrolling welcome text
#     for idx in range(-1 * (LINE_CHARS*HEIGHT//8) + LINE_CHARS, len(message), LINE_CHARS):

#         # Clear only the text area with a rectangle (so no .fill(0))
#         oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)

#         # Figure out start and end of visible welcome message
#         start = max(idx, 0)
#         end = idx+(LINE_CHARS*HEIGHT//8)
#         visible_message = message[start:end]

#         # Spread visible_message over the available space
#         for idx2 in range(0, LINE_CHARS*HEIGHT//8, LINE_CHARS):
#             oled.text(visible_message[idx2:idx2+LINE_CHARS], TEXT_BASE, idx2 // LINE_CHARS * (HEIGHT // 8))
#         #     print(visible_message[idx2:idx2+LINE_CHARS])
#         # print('-'*LINE_CHARS)
#         oled.show()

#         # Sleep so it doesn't go too fast -> make another timer?
#         utime.sleep_ms(250)

#     oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)
#     oled.show()

def badge_mode(name):
    global oled

    mouth_toggle()

    name = name[:14]

    oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)
    # Place for 14 chars of name under each other
    # TODO center if there are only 7 chars
    # TODO maybe support more than 14 also?
    oled.line(TEXT_BASE, HEIGHT // 2 - 10, WIDTH, HEIGHT // 2 - 10, 1)
    oled.line(TEXT_BASE, HEIGHT // 2 + 10, WIDTH, HEIGHT // 2 + 10, 1)
    oled.text(name[:7], TEXT_BASE, HEIGHT // 2 - 8)
    oled.text(name[7:], TEXT_BASE, HEIGHT // 2 + 2)
    oled.show()

    mouth_toggle()

# def boot_on_core1(args=None):
#     global i2c, oled

#     print('[core1] drawing boot')
#     mouth_timer.init(freq=7, callback=mouth_toggle)
#     uasyncio.run(scrolling_welcome(NAME))
#     mouth_timer.deinit()
#     badge_mode(NAME)

# TODO trying to do this on the other core crashes the screen
#       _thread.start_new_thread(boot_on_core1, (None,))
# using a timer also works fine i guess, to not block repl (and whatever else)
# TODO lock on oled/i2c while booting?

print('[core0] drawing boot')

idx = -1 * (LINE_CHARS*HEIGHT//8) + LINE_CHARS
def scrolling_welcome_message(timer: Timer):
    global oled, idx, mouth_timer

    name = NAME
    message = WELCOME_MESSAGE.format(name)

    if idx == len(message):
        mouth_timer.deinit()
        timer.deinit()
        badge_mode(NAME)
        return

    # Clear only the text area with a rectangle (so no .fill(0))
    oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)

    # Figure out start and end of visible welcome message
    start = max(idx, 0)
    end = idx+(LINE_CHARS*HEIGHT//8)
    visible_message = message[start:end]

    # Spread visible_message over the available space
    for idx2 in range(0, LINE_CHARS*HEIGHT//8, LINE_CHARS):
        oled.text(visible_message[idx2:idx2+LINE_CHARS], TEXT_BASE, idx2 // LINE_CHARS * (HEIGHT // 8))
    #     print(visible_message[idx2:idx2+LINE_CHARS])
    # print('-'*LINE_CHARS)
    oled.show()

    idx += LINE_CHARS

welcome_timer = Timer()

print('[core1] drawing boot')
mouth_timer.init(freq=7, callback=mouth_toggle)
welcome_timer.init(freq=7, callback=scrolling_welcome_timer)
