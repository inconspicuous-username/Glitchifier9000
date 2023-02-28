import framebuf
import time

from zlib import decompress
from binascii import a2b_base64
from machine import Timer

from graphics import OLED_WIDTH, OLED_HEIGHT
from debug import print_debug

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

HEAD = [
    # Closed
    'eJxtkL1OwzAQx8+xVXvqMWZAuEysGRFD8wi8QphYeQBE3CfoI/AqZupYRkaLAUY8erBSLo4TVU1+sk/2/e372t7sj493WgI458MZPuGIDeEm/CRYYHylrqqnHZes4wwSFbD2tECNQqz0knJqQZbeWgOsAA5nMC4RUWcQ5ZgEQJK7HhnEpN0e9PNeP3w2TVOVShRwiaFlLGVL1jmTuHhj/RtCcoovB4DbGNwoeh+795SQIIsZulB79/mVC9dryT98KYpUF2OglBJjA8Z11Pjf77cFKHq6xLqggs2GNJXjoK56W9tZI4NcT8PuQvQ/4zl62v3pNYaXZvnvLBaV3/bhWhpp3r2n1ajlfJAD/3x+yS4=',
    # Open
    'eJxtkKtSxDAUhk+azCaKg6xgyKKwlQxi8wi8QlFYHoDZdFVlH4FXCWrlIpEZBEgiKzIpaXqZnW2/SY44f/Kfy+62OT3dSw5grWvPcAkb2UbsjJsFA4RuxHXxfKCcBEogUQDR3QoKGdvINaXTwHNnTAUkAwpnEMoRUY4g8qkIAI9pNTGISbs7ypdGPn6WZVnkgmVwSRVPZWK1FK2tEhdvjNsjpCT7sgC4862dROd8eJeyOR1rHtvrO0zUNcbxHsZXtr254vTD5SxLfRECQgg2DVDZEAf/+/02hKPSeh8GtJL8sI2aGH1QFn1UZjHIIKt52aH17me0Cd51wffZN9++lut/F16xfd3b6bjS8fYZLVHy5SIH/gGLBtBA',
]

HEAD_WIDTH = 72
HEAD_HEIGHT = 64
CHAR_HEIGHT = 8

TEXT_BASE = HEAD_WIDTH
LINE_SIZE = OLED_WIDTH - TEXT_BASE
LINE_CHARS = LINE_SIZE // CHAR_HEIGHT
TEXT_SPACE = LINE_SIZE // CHAR_HEIGHT * (OLED_HEIGHT // CHAR_HEIGHT)

def clear_text_area(oled):
    oled.rect(HEAD_WIDTH, 0, LINE_SIZE, OLED_HEIGHT, 0, True)

class BootAnimator():
    def __init__(self, oled):
        self.oled = oled
        
        self.mouth_timer = Timer()
        self.welcome_timer = Timer()

        self.head_state = 0
        self.message_idx = -1 * (LINE_CHARS * OLED_HEIGHT//CHAR_HEIGHT) + LINE_CHARS

        self.animating = False
        self.boot_done_cb = None
        self.name = ''
        
    def boot_animation_start(self, name, boot_done_cb):
        self.boot_done_cb = boot_done_cb
        self.name = name
        self.mouth_timer.init(freq=7, callback=self.mouth_toggle)
        self.welcome_timer.init(freq=7, callback=self.scrolling_welcome_message)

    def boot_animation_kill(self, wait_ms=0):
        # Have this function to kill the animation faster as well
        self.mouth_timer.deinit()
        self.welcome_timer.deinit()
        clear_text_area(self.oled)
        self.oled.show()
        self.animating = False

        time.sleep_ms(500)
        self.boot_done_cb()

    def mouth_toggle(self, timer=None):
        self.oled.blit(framebuf.FrameBuffer(decompress(a2b_base64(HEAD[self.head_state])), HEAD_WIDTH, HEAD_HEIGHT, framebuf.MONO_VLSB), 0, 0)
        self.oled.show()
        self.head_state ^= 1

    def scrolling_welcome_message(self, timer: Timer):
        self.animating = True

        message = WELCOME_MESSAGE.format(self.name)

        # deinit the timers once the entire message has been printed
        if self.message_idx == len(message):
            
            return self.boot_animation_kill(wait_ms=500)

        # Clear only the text area with a rectangle (so no .fill(0))
        clear_text_area(self.oled)

        # Figure out start and end of visible welcome message
        start = max(self.message_idx, 0)
        end = self.message_idx + (LINE_CHARS*OLED_HEIGHT//CHAR_HEIGHT)
        visible_message = message[start:end]

        # Spread visible_message over the available space
        for idx2 in range(0, LINE_CHARS*OLED_HEIGHT//CHAR_HEIGHT, LINE_CHARS):
            self.oled.text(visible_message[idx2:idx2+LINE_CHARS], TEXT_BASE, idx2 // LINE_CHARS * (OLED_HEIGHT // CHAR_HEIGHT))
        self.oled.show()

        self.message_idx += LINE_CHARS