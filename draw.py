import display

FORMATTING_CODES = {
    "bold": 1,
    "faint": 2,
    "italic": 3,
    "underline": 4,
    "blink": 5,
    "rapid_blink": 6,
    "inverse": 7,
    "hide": 8,
    "strikethrough": 9
}

class DrawText:
    def __init__(self, x1, y1, text, font: tuple[int] | tuple[str], bg: tuple[float] | None = None):
        if font and isinstance(font[0], str):
            font = tuple([FORMATTING_CODES[style] for style in font])
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + 1
        self.bg = bg

    def execute(self, scroll):
        display.draw_text((self.left, self.top - scroll), self.text, style=self.font, bg=self.bg)

class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    def execute(self, scroll):
        x = self.left
        y = self.top - scroll
        width = max(0, self.right - self.left)
        height = max(0, self.bottom - self.top)
        display.draw_rect((x, y), (width, height), self.color)