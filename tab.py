import layout
import parser
import display
import css
import url

DEFAULT_STYLE_SHEET = css.CSSParser(open("browser.css").read()).parse()

def cascade_priority(rule):
    selector, body = rule
    return selector.priority

def is_hidden(node):
    current = node
    while current is not None:
        if isinstance(current, parser.Element) and current.tag in layout.HIDDEN_ELEMENTS:
            return True
        current = current.parent
    return False


def is_focusable(node):
    if is_hidden(node):
        return False
    if node.attributes.get("type") == "hidden":
        return False
    if node.tag == "a" and "href" in node.attributes:
        return True
    elif "tabindex" in node.attributes:
        return True
    elif node.tag in ["input", "textarea", "select", "button"]:
        return True
    return False

class Tab:
    def __init__(self, tab_height):
        self.tab_height = tab_height
        self.scroll = 0
        self.focus = None
        self.url: url.URL = None
        self.history = []

    def draw(self, offset):
        self.loop()
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.tab_height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll - offset)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)

    def load(self, url: url.URL):
        self.history.append(url)
        self.focus = None
        self.url = url
        self.scroll = 0
        body = url.request()
        self.nodes = parser.HTMLParser(body).parse()
        author_rules = []
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
            author_rules.extend(css.CSSParser(body).parse())
        # author origin beats user agent origin regardless of specificity
        self.rules = sorted(DEFAULT_STYLE_SHEET, key=cascade_priority) \
                   + sorted(author_rules, key=cascade_priority)
        self.render()

    def render(self):
        css.style(self.nodes, self.rules)
        self.document = layout.DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        layout.paint_tree(self.document, self.display_list)

    def activate(self, elt: parser.HTMLNode):
        if elt.tag == "a" and "href" in elt.attributes:
            url = self.url.resolve(elt.attributes["href"])
            return self.load(url)
        elif elt.tag == "input":
            while elt:
                if elt.tag == "form" and "action" in elt.attributes:
                    return self.submit_form(elt)
                elt = elt.parent

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

        self.render()

    def enter(self):
        if not self.focus: return
        self.activate(self.focus)
    
    def submit_form(self, elt: parser.Element):
        inputs = [node for node in layout.tree_to_list(elt, [])
                  if isinstance(node, parser.Element)
                  and node.tag in ("input", "textarea")
                  and "name" in node.attributes]
        params = {}
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")
            params[name] = value

        url = self.url.resolve(elt.attributes["action"])
        url.params = params
        url.method = elt.attributes.get("method", "get")
        
        self.load(url)

    def loop(self):
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > self.document.height - self.tab_height:
            self.scroll = self.document.height - self.tab_height

    def handle_key(self, key):
        match key:
            case "\033[A":
                self.scroll -= 1
            case "\033[B":
                self.scroll += 1
            case "\012" | "\015":
                self.enter()
            case "\011":
                #forward tab
                self.advance_tab()
            case "\033[Z":
                #backward tab
                self.advance_tab(backward=True)
            case _:
                if self.focus and self.focus.tag in ("input", "textarea"):
                    if self.focus.attributes.get("value") is None:
                        self.focus.attributes["value"] = ""
                    if key == "\010" or key == "\177":
                        self.focus.attributes["value"] = self.focus.attributes["value"][:-1]
                        display.p("\033[K")
                    else:
                        self.focus.attributes["value"] += key
                    display.p("\a")
                    # display.cur((self.focus.layout.x + len(self.focus.attributes["value"]), self.focus.layout.y - self.scroll))
                    self.render()
                elif key == " ":
                    self.scroll += 10
