import select
import sys

from debug import print_debug

## No enum type in micropython
# https://github.com/micropython/micropython-lib/issues/269
def enum(**enums: int):
    return type('Enum', (), enums)

def get_stdin_byte_or_button_press(buttons, read_stdin=True) -> tuple:
    # Wait for a byte from stdin, or any button press
    # Probably not very power efficient way of doing it :(
    #
    # TODO: can probably do some fancy stuff to turn the buttons into io streams as well
    
    b = None
    button = None

    # Wait for input on stdin via select.poll, button press via buttons class
    spoll = select.poll()
    spoll.register(sys.stdin, select.POLLIN)
    buttons.recent = None # Clear any recent
    
    # Wait for byte on stdin, not sure if this waits in a power efficient way
    while spoll.poll(0) == [] and buttons.recent == None:
        pass

    if spoll.poll(0):
        # Have option to not read the byte so it can be part of input()
        if read_stdin:
            b = sys.stdin.read(1)
        else:
            b = True
    
    if buttons.recent:
        button = buttons.recent
        buttons.recent = None

    # Not sure if this is needed
    spoll.unregister(sys.stdin)

    print_debug(f'{(b, button)=}')

    return (b, button)