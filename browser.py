import display
import lexer
import url
import layout

class Browser:
    def __init__(self):
        self.scroll = 0
    
    def draw(self, display_list):
        if self.scroll > self.layout.max_scroll:
            self.scroll = self.layout.max_scroll
        viewport_height = display.size[1]
        display.reset()
        for x, y, c, f in display_list:
            if y < self.scroll: continue
            if y >= self.scroll + viewport_height: continue
            style = ()
            if f[0]:
                style = style + (1,)
            if f[1]:
                style = style + (3,)
            display.draw_text((x, y - self.scroll), c, style=style)
        
        display.render()

    def load(self, url: url.URL):
        text = lexer.lex(url.request())
        self.layout = layout.Layout(text)
        self.draw(self.layout.display_list)
    
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
            if self.scroll > self.layout.max_scroll:
                self.scroll = self.layout.max_scroll
            self.draw(self.layout.display_list)
