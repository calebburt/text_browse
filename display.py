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

CHAR_WIDTH = 8
CHAR_HEIGHT = 16

def __getattr__(name):
    if name == "width":
        from layout import width_to_chars
        return width_to_chars(size[0] * CHAR_WIDTH)
    if name == "height":
        from layout import height_to_lines
        return height_to_lines(size[1] * CHAR_HEIGHT)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def reset():
    global display_list
    display_list = []

def render():
    global size
    width, height = size
    # build the whole frame as one string: clearing with an in-band escape
    # instead of os.system() and writing once means no blank frame between
    # clear and repaint; ?2026 makes it fully atomic where supported
    buf = ["\033[?2026h", "\033[2J", "\033[H"]
    for pos, color, bg, style, text in display_list:
        x, y = pos
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if x + len(text) <= 0:
            continue
        buf.append(f"\033[{y+1};{x+1}H\033[0m" + "".join(f"\033[{s}m" for s in style))
        if color:
            buf.append("\033[38;2;%d;%d;%dm" % tuple(int(v * 255) for v in color))
        if bg:
            buf.append("\033[48;2;%d;%d;%dm" % tuple(int(v * 255) for v in bg))
        buf.append(text[:width - x])  # clip so the terminal never auto-wraps
    buf.append("\033[0m")
    buf.append("\033[?2026l")
    sys.stdout.write("".join(buf))
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