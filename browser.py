import display
import parser
import css
import layout

DEFAULT_STYLE_SHEET = css.CSSParser(open("browser.css").read()).parse()

def cascade_priority(rule):
    selector, body = rule
    return selector.priority

def is_focusable(node):
    if node.tag == "a" and "href" in node.attributes:
        return True
    elif "tabindex" in node.attributes:
        return True
    elif node.tag in ["input", "textarea", "select", "button"]:
        return True
    return False

class Browser:
    def __init__(self):
        self.scroll = 0
        self.focus = None
        self.url = None
        display.p("\033[?1049h") # Switch to alternate screen buffer
    
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
        self.focus = None
        self.url = url
        self.scroll = 0
        body = url.request()
        self.nodes = parser.HTMLParser(body).parse()
        self.rules = DEFAULT_STYLE_SHEET.copy()
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
            self.rules.extend(css.CSSParser(body).parse())
        css.style(self.nodes, sorted(self.rules, key=cascade_priority))
        self.document = layout.DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        layout.paint_tree(self.document, self.display_list)
        self.draw()

    def activate(self, elt):
        if elt.tag == "a" and "href" in elt.attributes:
            url = self.url.resolve(elt.attributes["href"])
            return self.load(url)

    def advance_tab(self, backward=False):
        focusable_nodes = [node
            for node in layout.tree_to_list(self.nodes, [])
            if isinstance(node, parser.Element) and is_focusable(node)]
        focusable_nodes.sort(key=lambda node: int(node.attributes.get("tabindex", "9999999") if int(node.attributes.get("tabindex", "9999999")) >= 0 else 9999999))
        
        if self.focus in focusable_nodes:
            if backward:
                dir = -1
            else:
                dir = 1
            idx = focusable_nodes.index(self.focus) + dir
        else:
            idx = 0
        
        if idx >= len(focusable_nodes):
            idx = 0
        elif idx < 0:
            idx = len(focusable_nodes) - 1

        if self.focus:
            self.focus.is_focused = False
        self.focus = focusable_nodes[idx]
        self.focus.is_focused = True
    
    def enter(self):
        if not self.focus: return
        self.activate(self.focus)
    
    def loop(self):
        while True:
            key = display.read_key()
            match key:
                case "\033[A":
                    self.scroll -= 1
                case "\033[B":
                    self.scroll += 1
                case " ":
                    self.scroll += 10
                case "\012" | "\015":
                    self.enter()
                case "\011":
                    #forward tab
                    self.advance_tab()
                case "\033[Z":
                    #backward tab
                    self.advance_tab(backward=True)
                case "q" | "\003":
                    display.show_cursor()
                    display.p("\033[?1049l") # Switch back to normal screen buffer
                    return
            if self.scroll < 0:
                self.scroll = 0
            if self.scroll > self.document.max_scroll:
                self.scroll = self.document.max_scroll
            self.draw()
