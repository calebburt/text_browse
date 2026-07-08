import display
import parser
import draw

WIDTH, HEIGHT = display.size[0], display.size[1]

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = WIDTH
        self.x = 0
        self.y = 0
        child.layout()
        self.display_list = child.display_list
        self.height = child.height
        self.max_scroll = self.height
    
    def paint(self):
        return [draw.DrawRect(0, 0, self.width, self.height, (0, 0, 0))]

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node: parser.HTMLNode = node
        self.parent: BlockLayout | DocumentLayout = parent
        self.previous: BlockLayout = previous
        self.children: list[BlockLayout] = []
        self.display_list = []
        self.x: int = None
        self.y: int = None
        self.width: int = None
        self.height: int = None
        self.pre: bool = False
        
    def layout(self):
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y
        self.x = self.parent.x
        self.width = self.parent.width

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.b = False
            self.i = False
            self.pre = False

            self.line = []
            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def recurse(self, tree):
        if isinstance(tree, parser.Text):
            if self.pre:
                for line in tree.text.split('\n'):
                    self.line.append((self.cursor_x, line, (self.b, self.i)))
                    self.flush()
            else:
                for word in tree.text.split():
                    self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)
    
    def layout_mode(self):
        if isinstance(self.node, parser.Text):
            return "inline"
        elif any([isinstance(child, parser.Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"
    
    def word(self, word: str):
        toks = word.split()
        for word in toks:
            w = len(word)
            if self.cursor_x > 0 and self.cursor_x + w + 1 > self.width:
                self.flush()
            self.line.append((self.cursor_x, word, (self.b, self.i)))
            self.cursor_x += w + 1

    def flush(self):
        if not self.line: return
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + self.cursor_y
            self.display_list.append((x, y, word, font))
        self.cursor_x = 0
        self.cursor_y += 1
        self.line = []
    
    def open_tag(self, tag):
        if tag == "i":
            self.i = True
        elif tag == "b":
            self.b = True
        elif tag == "pre":
            self.pre = True
            self.flush()
        elif tag == "br":
            self.flush()
        elif tag == "hr":
            self.flush()
            self.line.append((0, "\u2500" * self.width, (False, False)))
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.i = False
        elif tag == "b":
            self.b = False
        elif tag == "pre":
            self.flush()
            self.pre = False
        elif tag == "p":
            self.flush()
            self.cursor_y += 1
    
    def paint(self):
        cmds = []
        if isinstance(self.node, parser.Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = draw.DrawRect(self.x, self.y, x2, y2, (0.5, 0.5, 0.5))
            cmds.append(rect)
        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                style = []
                if font[0]:
                    style.append("bold")
                if font[1]:
                    style.append("italic")
                cmds.append(draw.DrawText(x, y, word, style))
        return cmds
