DEBUG = False

def print_debug(fstr):
    if DEBUG:
        print('[DEBUG] ' + fstr)
    else:
        pass

def write_debug():
    with open('/data/debug', 'wb') as f:
        f.write(bytearray([DEBUG]))

def read_debug():
    global DEBUG
    with open('/data/debug', 'rb') as f:
        DEBUG = bool(f.read()[0])

def toggle_debug():
    global DEBUG
    DEBUG ^= 1
    write_debug()

try:
    read_debug()
except:
    write_debug()