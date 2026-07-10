import display
import parser
import css
import layout

DEFAULT_STYLE_SHEET = css.CSSParser(open("browser.css").read()).parse()

def cascade_priority(rule):
    selector, body = rule
    return selector.priority

class Browser:
    def __init__(self):
        self.scroll = 0
    
    def draw(self):
        if self.scroll > self.document.max_scroll:
            self.scroll = self.document.max_scroll
        viewport_height = display.size[1]
        display.reset()
        for cmd in self.display_list:
            if cmd.top > self.scroll + viewport_height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll)
        
        display.render()

    def load(self, url):
        body = url.request()
        self.nodes = parser.HTMLParser(body).parse()
        rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"]
             for node in layout.tree_to_list(self.nodes, [])
             if isinstance(node, parser.Element)
             and node.tag == "link"
             and node.attributes.get("rel") == "stylesheet"
             and "href" in node.attributes]
        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(css.CSSParser(body).parse())
        css.style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = layout.DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        layout.paint_tree(self.document, self.display_list)
        self.draw()
    
    def loop(self):
        while True:
            key = display.read_key()
            match key:
                case "\033[A":
                    self.scroll -= 1
                case "\033[B":
                    self.scroll += 1
                case _:
                    display.show_cursor()
                    print()
                    return
            if self.scroll < 0:
                self.scroll = 0
            if self.scroll > self.document.max_scroll:
                self.scroll = self.document.max_scroll
            self.draw()
