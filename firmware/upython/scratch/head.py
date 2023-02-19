import utime
import framebuf
import _thread
import os

from zlib import decompress
from binascii import a2b_base64

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, Timer

HEAD = [
    # Closed
    b'eJxtkL1OwzAQx8+xVXvqMWZAuEysGRFD8wi8QphYeQBE3CfoI/AqZupYRkaLAUY8erBSLo4TVU1+sk/2/e372t7sj493WgI458MZPuGIDeEm/CRYYHylrqqnHZes4wwSFbD2tECNQqz0knJqQZbeWgOsAA5nMC4RUWcQ5ZgEQJK7HhnEpN0e9PNeP3w2TVOVShRwiaFlLGVL1jmTuHhj/RtCcoovB4DbGNwoeh+795SQIIsZulB79/mVC9dryT98KYpUF2OglBJjA8Z11Pjf77cFKHq6xLqggs2GNJXjoK56W9tZI4NcT8PuQvQ/4zl62v3pNYaXZvnvLBaV3/bhWhpp3r2n1ajlfJAD/3x+yS4=',
    # Open
    b'eJxtkKtSxDAUhk+azCaKg6xgyKKwlQxi8wi8QlFYHoDZdFVlH4FXCWrlIpEZBEgiKzIpaXqZnW2/SY44f/Kfy+62OT3dSw5grWvPcAkb2UbsjJsFA4RuxHXxfKCcBEogUQDR3QoKGdvINaXTwHNnTAUkAwpnEMoRUY4g8qkIAI9pNTGISbs7ypdGPn6WZVnkgmVwSRVPZWK1FK2tEhdvjNsjpCT7sgC4862dROd8eJeyOR1rHtvrO0zUNcbxHsZXtr254vTD5SxLfRECQgg2DVDZEAf/+/02hKPSeh8GtJL8sI2aGH1QFn1UZjHIIKt52aH17me0Cd51wffZN9++lut/F16xfd3b6bjS8fYZLVHy5SIH/gGLBtBA',
]
HEAD_WIDTH = 72
HEAD_HEIGHT = 64

# Toggle mouth, no need to clear every draw, draw over it with blit
# TODO: could optimize by only drawing the mouth? probably most of the overhead is sending the updated framebuf, so probably won't matter
head_state = 0
def mouth_toggle(timer):
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


WELCOME_MESSAGE = (
    b"{:<14}"
    b"       "
    b"-------"
    b"       "
    b"On be- "
    b"half of"
    b"the Or-"
    b"gani-  "
    b"zers of"
    b"the    "
    b"Riscure"
    b"Federa-"
    b"tion of"
    b"Enter- "
    b"tainers"
    b"and    "
    b"Funny  "
    b"Endea- "
    b"vors,  "
    b"welcome"
    b"to the "
    b"fifth  "
    b"volume "
    b"of     "
    b"riscu- "
    b"fefe!  ")

i2c = I2C(1, sda=Pin(26), scl=Pin(27))
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)


# for idx in range(0, len(WELCOME_MESSAGE), LINE_CHARS): 
#     print(WELCOME_MESSAGE[idx:idx+LINE_CHARS].decode())

# for idx in range(0, LINE_CHARS * (HEIGHT // 8), LINE_CHARS): 
#     oled.text(WELCOME_MESSAGE[idx:idx+LINE_CHARS], TEXT_BASE, idx // LINE_CHARS * (HEIGHT // 8)); 
#     oled.show(); 
#     utime.sleep_ms(500)

for idx in range(-1 * (LINE_CHARS*HEIGHT//8) + LINE_CHARS, len(WELCOME_MESSAGE), LINE_CHARS):
    start = max(idx, 0)
    end = idx+(LINE_CHARS*HEIGHT//8)
    # print(start,end)
    visible = WELCOME_MESSAGE[start:end]
    for idx2 in range(0, LINE_CHARS*HEIGHT//8, LINE_CHARS): 
        print(visible[idx2:idx2+LINE_CHARS].decode())
    print('-'*LINE_CHARS)

# Start the mouth movement, 10Hz
mouth_timer.init(freq=7, callback=mouth_toggle)

def scrolling_welcome(name):
    global oled

    name = name[:14]
    message = WELCOME_MESSAGE.format(name)

    # Draw scrolling welcome text
    for idx in range(-1 * (LINE_CHARS*HEIGHT//8) + LINE_CHARS, len(message), LINE_CHARS):

        # Clear only the text area with a rectangle (so no .fill(0))
        oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)

        # Figure out start and end of visible welcome message
        start = max(idx, 0)
        end = idx+(LINE_CHARS*HEIGHT//8)
        visible_message = message[start:end]

        # Spread visible_message over the available space
        for idx2 in range(0, LINE_CHARS*HEIGHT//8, LINE_CHARS):
            oled.text(visible_message[idx2:idx2+LINE_CHARS], TEXT_BASE, idx2 // LINE_CHARS * (HEIGHT // 8))
            print(visible_message[idx2:idx2+LINE_CHARS])
        oled.show()
        print('-' * LINE_CHARS)

        # Sleep so it doesn't go too fast -> make another timer?
        utime.sleep_ms(250)

    oled.rect(HEAD_WIDTH, 0, LINE_SIZE, HEIGHT, 0, True)
    oled.show()

def badge_mode(name):
    global oled

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

scrolling_welcome(b'Quorth')
mouth_timer.deinit()

badge_mode(b'Quorth')
