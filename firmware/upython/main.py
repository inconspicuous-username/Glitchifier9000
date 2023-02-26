from enum import Enum, auto
import signal

from ctf import ctf_main

class BadgeState(Enum):
    NAMETAG_SHOW = auto()
    NAMETAG_SET = auto()
    GLITCHIFIER9000 = auto()
    CTF = auto()
    REPL = auto()

    BOOT = auto()
    MENU = auto()

    IDLE = auto()

    @staticmethod
    def menu_line():
        return '\n'.join(f' {x.value}: {x.name}' for x in [
                BadgeState.NAMETAG_SHOW, 
                BadgeState.NAMETAG_SET, 
                BadgeState.GLITCHIFIER9000, 
                BadgeState.CTF,
                BadgeState.REPL,
            ])


class Main():

    def __init__(self) -> None:
        self.state = BadgeState.BOOT

    def mainloop(self) -> None:
        while True:
            try:
                if self.state == BadgeState.BOOT:
                    print('TODO: draw boot animation')

                    self.state = BadgeState.MENU
                
                elif self.state == BadgeState.MENU:
                    print('TODO: X option menu')
                    print(BadgeState.menu_line())
                    selected = input('> ')
                    try:
                        selected = int(selected)
                        self.state = BadgeState(selected)
                    except ValueError:
                        print(f'Invalid selection "{selected}"')
                    
                elif self.state == BadgeState.NAMETAG_SHOW:
                    try: 
                        with open('name.txt', 'r') as f:
                            name = f.read()
                    except FileNotFoundError:
                        name = 'NONAME'
                    
                    print(f'Name: {name}')
                    self.state = BadgeState.IDLE
                    
                elif self.state == BadgeState.NAMETAG_SET:
                    with open('name.txt', 'w') as f:
                        name = input('name?\n> ')
                        f.write(name)
                    
                    self.state = BadgeState.NAMETAG_SHOW

                elif self.state == BadgeState.GLITCHIFIER9000:
                    print('TODO: enter Glitcher mode')

                    self.state = BadgeState.MENU
                
                elif self.state == BadgeState.IDLE:
                    print('TODO: idle in a mpy way')
                    signal.pause()
                
                elif self.state in [BadgeState.REPL, BadgeState.CTF]:
                    return self.state

                else:
                    self.state = BadgeState.MENU
            
            except KeyboardInterrupt:
                # Pretend there is a button with ctrl-c
                print('Button pressed')
                self.button_handle(0x1)

    def button_handle(self, interrupts) -> None:
        print('TODO: handle button press based on state')

        if interrupts & 1 == 1:
            self.state = BadgeState.MENU


if __name__ == '__main__':
    m = Main()
    exit_state = m.mainloop()

    if exit_state == BadgeState.CTF:
        ctf_main()
    elif exit_state == BadgeState.REPL:
        # drop to interpreter, happens automatically in mpy
        pass
