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

COLORS = {
    "aliceblue": (0.941, 0.973, 1.000),
    "antiquewhite": (0.980, 0.922, 0.843),
    "aqua": (0.000, 1.000, 1.000),
    "aquamarine": (0.498, 1.000, 0.831),
    "azure": (0.941, 1.000, 1.000),
    "beige": (0.961, 0.961, 0.863),
    "bisque": (1.000, 0.894, 0.769),
    "black": (0.000, 0.000, 0.000),
    "blanchedalmond": (1.000, 0.922, 0.804),
    "blue": (0.000, 0.000, 1.000),
    "blueviolet": (0.541, 0.169, 0.886),
    "brown": (0.647, 0.165, 0.165),
    "burlywood": (0.871, 0.722, 0.529),
    "cadetblue": (0.373, 0.620, 0.627),
    "chartreuse": (0.498, 1.000, 0.000),
    "chocolate": (0.824, 0.412, 0.118),
    "coral": (1.000, 0.498, 0.314),
    "cornflowerblue": (0.392, 0.584, 0.929),
    "cornsilk": (1.000, 0.973, 0.863),
    "crimson": (0.863, 0.078, 0.235),
    "cyan": (0.000, 1.000, 1.000),
    "darkblue": (0.000, 0.000, 0.545),
    "darkcyan": (0.000, 0.545, 0.545),
    "darkgoldenrod": (0.722, 0.525, 0.043),
    "darkgray": (0.663, 0.663, 0.663),
    "darkgreen": (0.000, 0.392, 0.000),
    "darkkhaki": (0.741, 0.718, 0.420),
    "darkmagenta": (0.545, 0.000, 0.545),
    "darkolivegreen": (0.333, 0.420, 0.184),
    "darkorange": (1.000, 0.549, 0.000),
    "darkorchid": (0.600, 0.196, 0.800),
    "darkred": (0.545, 0.000, 0.000),
    "darksalmon": (0.914, 0.588, 0.478),
    "darkseagreen": (0.561, 0.737, 0.561),
    "darkslateblue": (0.282, 0.239, 0.545),
    "darkslategray": (0.184, 0.310, 0.310),
    "darkturquoise": (0.000, 0.808, 0.820),
    "darkviolet": (0.580, 0.000, 0.827),
    "deeppink": (1.000, 0.078, 0.576),
    "deepskyblue": (0.000, 0.749, 1.000),
    "dimgray": (0.412, 0.412, 0.412),
    "dodgerblue": (0.118, 0.565, 1.000),
    "firebrick": (0.698, 0.133, 0.133),
    "floralwhite": (1.000, 0.980, 0.941),
    "forestgreen": (0.133, 0.545, 0.133),
    "fuchsia": (1.000, 0.000, 1.000),
    "gainsboro": (0.863, 0.863, 0.863),
    "ghostwhite": (0.973, 0.973, 1.000),
    "gold": (1.000, 0.843, 0.000),
    "goldenrod": (0.855, 0.647, 0.125),
    "gray": (0.502, 0.502, 0.502),
    "green": (0.000, 0.502, 0.000),
    "greenyellow": (0.678, 1.000, 0.184),
    "honeydew": (0.941, 1.000, 0.941),
    "hotpink": (1.000, 0.412, 0.706),
    "indianred": (0.804, 0.361, 0.361),
    "indigo": (0.294, 0.000, 0.510),
    "ivory": (1.000, 1.000, 0.941),
    "khaki": (0.941, 0.902, 0.549),
    "lavender": (0.902, 0.902, 0.980),
    "lavenderblush": (1.000, 0.941, 0.961),
    "lawngreen": (0.486, 0.988, 0.000),
    "lemonchiffon": (1.000, 0.980, 0.804),
    "lightblue": (0.678, 0.847, 0.902),
    "lightcoral": (0.941, 0.502, 0.502),
    "lightcyan": (0.878, 1.000, 1.000),
    "lightgoldenrodyellow": (0.980, 0.980, 0.824),
    "lightgray": (0.827, 0.827, 0.827),
    "lightgreen": (0.565, 0.933, 0.565),
    "lightpink": (1.000, 0.714, 0.757),
    "lightsalmon": (1.000, 0.627, 0.478),
    "lightseagreen": (0.125, 0.698, 0.667),
    "lightskyblue": (0.529, 0.808, 0.980),
    "lightslategray": (0.467, 0.533, 0.600),
    "lightsteelblue": (0.690, 0.769, 0.871),
    "lightyellow": (1.000, 1.000, 0.878),
    "lime": (0.000, 1.000, 0.000),
    "limegreen": (0.196, 0.804, 0.196),
    "linen": (0.980, 0.941, 0.902),
    "magenta": (1.000, 0.000, 1.000),
    "maroon": (0.502, 0.000, 0.000),
    "mediumaquamarine": (0.400, 0.804, 0.667),
    "mediumblue": (0.000, 0.000, 0.804),
    "mediumorchid": (0.729, 0.333, 0.827),
    "mediumpurple": (0.576, 0.439, 0.859),
    "mediumseagreen": (0.235, 0.702, 0.443),
    "mediumslateblue": (0.482, 0.408, 0.933),
    "mediumspringgreen": (0.000, 0.980, 0.604),
    "mediumturquoise": (0.282, 0.820, 0.800),
    "mediumvioletred": (0.780, 0.082, 0.522),
    "midnightblue": (0.098, 0.098, 0.439),
    "mintcream": (0.961, 1.000, 0.980),
    "mistyrose": (1.000, 0.894, 0.882),
    "moccasin": (1.000, 0.894, 0.710),
    "navajowhite": (1.000, 0.871, 0.678),
    "navy": (0.000, 0.000, 0.502),
    "oldlace": (0.992, 0.961, 0.902),
    "olive": (0.502, 0.502, 0.000),
    "olivedrab": (0.420, 0.557, 0.137),
    "orange": (1.000, 0.647, 0.000),
    "orangered": (1.000, 0.271, 0.000),
    "orchid": (0.855, 0.439, 0.839),
    "palegoldenrod": (0.933, 0.910, 0.667),
    "palegreen": (0.596, 0.984, 0.596),
    "paleturquoise": (0.686, 0.933, 0.933),
    "palevioletred": (0.859, 0.439, 0.576),
    "papayawhip": (1.000, 0.937, 0.835),
    "peachpuff": (1.000, 0.855, 0.725),
    "peru": (0.804, 0.522, 0.247),
    "pink": (1.000, 0.753, 0.796),
    "plum": (0.867, 0.627, 0.867),
    "powderblue": (0.690, 0.878, 0.902),
    "purple": (0.502, 0.000, 0.502),
    "rebeccapurple": (0.400, 0.200, 0.600),
    "red": (1.000, 0.000, 0.000),
    "rosybrown": (0.737, 0.561, 0.561),
    "royalblue": (0.255, 0.412, 0.882),
    "saddlebrown": (0.545, 0.271, 0.075),
    "salmon": (0.980, 0.502, 0.447),
    "sandybrown": (0.957, 0.643, 0.376),
    "seagreen": (0.180, 0.545, 0.341),
    "seashell": (1.000, 0.961, 0.933),
    "sienna": (0.627, 0.322, 0.176),
    "silver": (0.753, 0.753, 0.753),
    "skyblue": (0.529, 0.808, 0.922),
    "slateblue": (0.416, 0.353, 0.804),
    "slategray": (0.439, 0.502, 0.565),
    "snow": (1.000, 0.980, 0.980),
    "springgreen": (0.000, 1.000, 0.498),
    "steelblue": (0.275, 0.510, 0.706),
    "tan": (0.824, 0.706, 0.549),
    "teal": (0.000, 0.502, 0.502),
    "thistle": (0.847, 0.749, 0.847),
    "tomato": (1.000, 0.388, 0.278),
    "turquoise": (0.251, 0.878, 0.816),
    "violet": (0.933, 0.510, 0.933),
    "wheat": (0.961, 0.871, 0.702),
    "white": (1.000, 1.000, 1.000),
    "whitesmoke": (0.961, 0.961, 0.961),
    "yellow": (1.000, 1.000, 0.000),
    "yellowgreen": (0.604, 0.804, 0.196),

    "transparent": None
}

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
        return []

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
        if isinstance(self.node, parser.Element):
            bgcolor = self.node.style.get("background-color", "transparent")
        else:
            bgcolor = self.node.parent.style.get("background-color", "transparent")
        x2, y2 = self.x + self.width, self.y + self.height
        rect = draw.DrawRect(self.x, self.y, x2, y2, COLORS[bgcolor])
        cmds.append(rect)
        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                style = []
                if font[0]:
                    style.append("bold")
                if font[1]:
                    style.append("italic")
                cmds.append(draw.DrawText(x, y, word, style, COLORS[bgcolor]))
        return cmds
