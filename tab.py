import layout
import parser
import display
import css
import url
import js
import tasks

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
        self.js: js.JSContext = None
        self.url: url.URL = None
        self.history = []
        self.task_runner = tasks.TaskRunner(self)

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

    def load(self, url_: url.URL):
        self.history.append(url)
        self.focus = None
        self.url = url_
        self.scroll = 0
        headers, body = url_.request(cross_origin=url_.host != self.url.host)
        self.nodes = parser.HTMLParser(body).parse()

        self.allowed_origins = None
        if "content-security-policy" in headers:
            csp = headers["content-security-policy"].split()
            if len(csp) > 0 and csp[0] == "default-src":
                self.allowed_origins = []
                for origin in csp[1:]:
                    try:
                        self.allowed_origins.append(url.URL(origin).origin())
                    except:
                        pass

        scripts = [node for node
                   in layout.tree_to_list(self.nodes, [])
                   if isinstance(node, parser.Element)
                   and node.tag == "script"]
        if self.js: self.js.discarded = True
        self.js = js.JSContext(self) # new context for every page load
        for script in scripts:
            if "src" in script.attributes:
                script_url = url_.resolve(script.attributes["src"])
                if not self.allowed_request(script_url):
                    # log csp breach
                    js.log_file.write(f"CSP blocked script load from {script_url}\n")
                    continue
                try:
                    _, body = script_url.request(cross_origin=script_url.host != self.url.host)
                except:
                    continue
            else:
                body = script.children[0].text # text child
            
            task = tasks.Task(self.js.run, body)
            self.task_runner.schedule_task(task)

        author_rules = []
        links = [node.attributes["href"]
             for node in layout.tree_to_list(self.nodes, [])
             if isinstance(node, parser.Element)
             and node.tag == "link"
             and node.attributes.get("rel") == "stylesheet"
             and "href" in node.attributes]
        for link in links:
            style_url = url_.resolve(link)
            try:
                _, body = style_url.request(cross_origin=style_url.host != self.url.host)
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
        if self.js.dispatch_event("click", elt): return

        if elt.tag == "a" and "href" in elt.attributes:
            url = self.url.resolve(elt.attributes["href"])
            return self.load(url)
        elif elt.tag in ["input", "button"]: # enter on any input submits the form
            while elt:
                if elt.tag == "form" and "action" in elt.attributes:
                    return self.submit_form(elt)
                elt = elt.parent

    def node_bounds(self, nodes):
        """id(node) -> (top, bottom) rows spanned; nodes hidden by CSS
        (display: none) have no layout objects and get no entry."""
        ids = {id(node) for node in nodes}
        bounds = {}
        for obj in layout.tree_to_list(self.document, []):
            current = getattr(obj, "node", None)
            while current is not None:
                if id(current) in ids:
                    top, bottom = bounds.get(id(current), (obj.y, obj.y + obj.height))
                    bounds[id(current)] = (min(top, obj.y), max(bottom, obj.y + obj.height))
                current = current.parent
        return bounds

    def scroll_to(self, node):
        bounds = self.node_bounds([node]).get(id(node))
        if not bounds: return
        top, bottom = bounds
        if top < self.scroll:
            self.scroll = top
        elif bottom > self.scroll + self.tab_height:
            self.scroll = min(top, bottom - self.tab_height)

    def advance_tab(self, backward=False):
        focusable_nodes = [node
            for node in layout.tree_to_list(self.nodes, [])
            if isinstance(node, parser.Element) and is_focusable(node)]
        focusable_nodes.sort(key=lambda node: int(node.attributes.get("tabindex", "9999999") if int(node.attributes.get("tabindex", "9999999")) >= 0 else 9999999))
        
        # CSS-hidden nodes get no bounds entry and must be skipped, or
        # tabbing gets stuck cycling the links before them
        bounds = self.node_bounds(focusable_nodes)
        focusable_nodes = [node for node in focusable_nodes if id(node) in bounds]
        if not focusable_nodes: return

        def visible(node):
            top, bottom = bounds[id(node)]
            return top < self.scroll + self.tab_height and bottom > self.scroll

        dir = -1 if backward else 1
        in_view = [node for node in focusable_nodes if visible(node)]
        if self.focus in focusable_nodes and (visible(self.focus) or not in_view):
            new_focus = focusable_nodes[(focusable_nodes.index(self.focus) + dir) % len(focusable_nodes)]
        elif in_view:
            # the old focus scrolled out of view (or nothing was focused):
            # the topmost focusable in the viewport takes focus, so scrolling
            # doubles as focus navigation on long pages
            new_focus = min(in_view, key=lambda node: bounds[id(node)][0])
        else:
            new_focus = focusable_nodes[0]

        if self.focus:
            self.focus.is_focused = False
        self.focus = new_focus
        self.focus.is_focused = True

        self.render()
        self.scroll_to(self.focus)

    def enter(self):
        if not self.focus: return
        self.activate(self.focus)
    
    def submit_form(self, elt: parser.Element):
        if self.js.dispatch_event("submit", elt): return

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

    def allowed_request(self, url):
        return self.allowed_origins == None or \
            url.origin() in self.allowed_origins

    def loop(self):
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > self.document.height - self.tab_height:
            self.scroll = self.document.height - self.tab_height
        self.task_runner.run()

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
                if self.focus:
                    if self.js.dispatch_event("keydown", self.focus): return
                
                if self.focus and self.focus.tag in ("input", "textarea"):
                    if self.focus.attributes.get("value") is None:
                        self.focus.attributes["value"] = ""
                    if key == "\010" or key == "\177":
                        self.focus.attributes["value"] = self.focus.attributes["value"][:-1]
                        display.p("\033[K")
                    else:
                        self.focus.attributes["value"] += key
                    display.p("\a")
                    self.render()
                    # display.cur((self.focus.layout.x + len(self.focus.attributes["value"]), self.focus.layout.y - self.scroll))
                elif key == " ":
                    self.scroll += 10
