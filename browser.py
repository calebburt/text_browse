import display
import parser
import url
import layout

class Browser:
    def __init__(self):
        self.scroll = 0
    
    def draw(self):
        if self.scroll > self.layout.max_scroll:
            self.scroll = self.layout.max_scroll
        viewport_height = display.size[1]
        display.reset()
        for x, y, c, f in self.display_list:
            if y < self.scroll: continue
            if y >= self.scroll + viewport_height: continue
            style = ()
            if f[0]:
                style = style + (1,)
            if f[1]:
                style = style + (3,)
            display.draw_text((x, y - self.scroll), c, style=style)
        
        display.render()

    def load(self, url):
        body = url.request()
        self.nodes = parser.HTMLParser(body).parse()
        self.layout = layout.Layout(self.nodes)
        self.display_list = self.layout.display_list
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
                    print()
                    return
            if self.scroll < 0:
                self.scroll = 0
            if self.scroll > self.layout.max_scroll:
                self.scroll = self.layout.max_scroll
            self.draw()
