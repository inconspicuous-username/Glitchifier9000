from machine import Timer

from graphics import OLED_HEIGHT, rotate_row_bytes, dec_to_framebuf

RISCUFEFE_IMPACT = b'eJxlisEJgDAUQzPGB5fwKCjoSHoTLLiG4xQ8uEZHKHgJfPFb2oOgOSQ8XkjWDaCqQCQ3mUcgRIowBoBkKblNq+o1XzYzpOSZzuOw2wH9at5frgNWMz9kWY7J7Lsu7Y8fxWpPCA=='
RISCUFEFE_IMPACT_HEIGHT = 16
RISCUFEFE_IMPACT_WIDTH = 72

def read_namefile():
    try: 
        with open('name.txt', 'r') as f:
            return f.read()
    except:
        return 'NONAME'

def write_namefile(name):
    with open('name.txt', 'w') as f:
        f.write(name)

class NametagAnimator():
    def __init__(self, oled):
        self.oled = oled
        self.rotate_timer = Timer()
        self.animating = False
        
    def banner_rotate_timer(self, timer: Timer):
        rotate_row_bytes(self.oled.buffer, 0, True)
        rotate_row_bytes(self.oled.buffer, 1, True)
        rotate_row_bytes(self.oled.buffer, 6, False)
        rotate_row_bytes(self.oled.buffer, 7, False)
        self.oled.show()

    def kill(self):
        self.rotate_timer.deinit()
        self.animating = False

    def name_to_oled(self, name):
        self.name = name
        self.oled.fill(0)

        # Add banner to top and bottom
        banner = dec_to_framebuf(RISCUFEFE_IMPACT, RISCUFEFE_IMPACT_WIDTH, RISCUFEFE_IMPACT_HEIGHT)
        self.oled.blit(banner, 0, 0)
        self.oled.blit(banner, 0, OLED_HEIGHT-RISCUFEFE_IMPACT_HEIGHT)

        self.oled.text(self.name, 8, 28)
        self.oled.show()

        # Set up rotation timer for banner rotations
        self.rotate_timer.init(freq=20, callback=self.banner_rotate_timer)
        self.animating = True
