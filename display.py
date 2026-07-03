import shutil
import os, sys
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

p = sys.stdout.write

def cls():
    os.system("clear")

def home():
    p("\033[H")

def cur(pos):
    x, y = pos
    p(f"\033[{y+1};{x+1}H")

def col(color: tuple[float, float, float]):
    color: tuple[int, int, int] = tuple([int(c * 255) for c in color])
    p(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")

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

def render(scroll=0):
    buffer = [[" " for _ in range(size[0])] for _ in range(size[1])]
    for pos, color, style, text in display_list:
        x, y = pos
        row = y - scroll
        if 0 <= x < size[0] and 0 <= row < size[1]:
            buffer[row][x] = text
    hide_cursor()
    cls()
    p("\n".join("".join(row) for row in buffer))
    p("\033[H")
    show_cursor()
    sys.stdout.flush()

def draw_text(pos: tuple[int, int], text: str, color: tuple[float, float, float]=(1, 1, 1,), style: tuple[int]=()):
    display_list.append((pos, color, style, text))
    