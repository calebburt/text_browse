import display

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c

    return text

class Browser:
    def __init__(self):
        self.display_list = []
        self.scroll = 0

    def layout(self, text):
        self.display_list = []
        WIDTH, HEIGHT = display.size[0], display.size[1]
        cursor_x, cursor_y = 0, 0
        for c in text:
            self.display_list.append((cursor_x, cursor_y, c))
            cursor_x += 1
            if cursor_x >= WIDTH:
                cursor_y += 1
                cursor_x = 0
        self.max_scroll = max(0, cursor_y - HEIGHT + 1)
    
    def draw(self):
        if self.scroll > getattr(self, 'max_scroll', 0):
            self.scroll = self.max_scroll
        display.reset()
        for x, y, c in self.display_list:
            if y < self.scroll: continue
            if y >= self.scroll + display.size[1]: continue
            display.draw_text((x, y), c)
        
        display.render(self.scroll)

    def load(self, url):
        text = lex(url.request())
        self.layout(text)
        self.draw()
    
    def loop(self):
        while True:
            key = display.read_key()
            match key:
                case "\033[A":
                    self.scroll -= 1
                case "\033[B":
                    self.scroll += 1
                # case "\033[C":
                #     print("RIGHT")
                # case "\033[D":
                #     print("LEFT")
                case _:
                    display.show_cursor()
                    return
            if self.scroll < 0:
                self.scroll = 0
            if self.scroll > getattr(self, 'max_scroll', 0):
                self.scroll = self.max_scroll
            self.draw()
