import shutil
import os, sys

if os.name == "nt":
    import msvcrt

    def read_key():
        ch = msvcrt.getch()

        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()

            key_map = {
                b'H': '\033[A',  # Up
                b'P': '\033[B',  # Down
                b'M': '\033[C',  # Right
                b'K': '\033[D',  # Left
            }

            return key_map.get(ch2, (ch + ch2).decode(errors="ignore"))

        return ch.decode('utf-8', errors='ignore')

    def cls():
        os.system("cls")

else:
    import tty
    import termios

    def read_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)

            if ch1 == '\033':
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                return ch1 + ch2 + ch3

            return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    def cls():
        os.system("clear")


p = sys.stdout.write

def home():
    p("\033[H")

def cur(pos):
    x, y = pos
    p(f"\033[{y+1};{x+1}H")

def col(color: tuple[float, float, float]):
    color: tuple[int, int, int] = tuple([int(c * 255) for c in color])
    p(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")
def back(color: tuple[float, float, float]):
    color: tuple[int, int, int] = tuple([int(c * 255) for c in color])
    p(f"\033[48;2;{color[0]};{color[1]};{color[2]}m")

def stl(styles: tuple[KeyboardInterrupt]):
    rst()
    for s in styles:
        p(f"\033[{s}m")

def rst():
    p("\033[0m")

def hide_cursor():
    p("\033[?25l")

def show_cursor():
    p("\033[?25h")


size: tuple[int, int] = shutil.get_terminal_size(fallback=(80, 24))
display_list: list[tuple[tuple[int, int], tuple[float, float, float], tuple[int], str]] = []

def reset():
    global display_list
    display_list = []
    show_cursor()

def render():
    hide_cursor()
    cls()
    global size
    width, height = size
    for pos, color, bg, style, text in display_list:
        x, y = pos
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if x + len(text) <= 0 or x >= width:
            continue
        cur(pos)
        stl(style)
        if color != None:
            col(color)
        if bg != None:
            back(bg)
        p(text)
        rst()
    sys.stdout.flush()
    size = shutil.get_terminal_size(fallback=(80, 24))

def draw_text(pos: tuple[int, int], text: str, color: tuple[float, float, float]=(1, 1, 1,), style: tuple[int]=(), bg: tuple[float, float, float]=None):
    display_list.append((pos, color, bg, style, text))


def draw_rect(pos: tuple[int, int], size: tuple[int, int], color: tuple[float, float, float]=(1, 1, 1,)):
    if color != None:
        x, y = pos
        width, height = size
        if width <= 0 or height <= 0:
            return

        fill = " " * width
        for row in range(height):
            draw_text((x, y + row), fill, bg=color)