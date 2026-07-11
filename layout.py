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

HIDDEN_ELEMENTS = [
    "script", "style", "meta", "link", "head", "title"
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
}

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

def color_to_tuple(color: str):
    if color in COLORS: 
        return COLORS[color]
    elif color[0] == "#":
        color = color.lstrip('#')
        if len(color) == 3:
            color = ''.join(char * 2 for char in color)
        return tuple(round(int(color[i:i+2], 16) / 255.0, 3) for i in (0, 2, 4))

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
    
    def paint(self):
        return []
    
class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
    
    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y
        
        for word in self.children:
            word.layout()
            word.y = self.y

        if not self.children:
            self.height = 0
            return
        else:
            self.height = 1

        text_align = self.node.style.get("text-align", "left")

        if text_align in ("center", "right"):
            # total width of all words including spaces between them
            total_width = sum(len(child.word) + 1 for child in self.children) - 1

            if text_align == "center":
                offset = (self.width - total_width) // 2
            else:  # "right"
                offset = self.width - total_width

            for child in self.children:
                child.x += offset
    
    def paint(self):
        return []

class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous
        self.x = None
        self.y = None
        self.width = None
        self.height = None
    
    def layout(self):
        self.width = len(self.word)

        if self.previous:
            self.x = self.previous.x + 1 + self.previous.width
        else:
            self.x = self.parent.x

        self.height = 1
    
    def paint(self):
        color = self.node.style["color"]
        bgcolor = self.node.parent.style.get("background-color", "transparent")
        font = self.node.style.get("font-weight", "normal") == "bold", self.node.style.get("font-style", "normal") == "italic"
        style = []
        if font[0]:
            style.append("bold")
        if font[1]:
            style.append("italic")
        return [draw.DrawText(self.x, self.y, self.word, style, color_to_tuple(bgcolor), color_to_tuple(color))]

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
        
    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.new_line()
            self.recurse(self.node)

        for child in self.children:
            child.layout()

        self.height = sum([child.height for child in self.children])

    def recurse(self, tree):
        if isinstance(tree, parser.Text):
            for word in tree.text.split():
                self.word(tree, word)
        else:
            if tree.tag in HIDDEN_ELEMENTS:
                return
            if tree.tag == "br":
                self.new_line()
            elif tree.tag == "hr":
                self.new_line()
                self.children[-1].children.append(TextLayout(tree, "\u2500" * self.width, self.children[-1], None))
                self.new_line()
            for child in tree.children:
                self.recurse(child)
    
    def layout_mode(self):
        if isinstance(self.node, parser.Text):
            return "inline"
        elif any([isinstance(child, parser.Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        return "inline"
    
    def word(self, node: parser.HTMLNode, word: str):
        toks = word.split()
        for word in toks:
            w = len(word)
            if self.cursor_x > 0 and self.cursor_x + w + 1 > self.width:
                self.new_line()
            self.cursor_x += w + 1
            line = self.children[-1]
            previous_word = line.children[-1] if line.children else None
            text = TextLayout(node, word, line, previous_word)
            line.children.append(text)

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)
    
    def paint(self):
        cmds = []
        if isinstance(self.node, parser.Element):
            bgcolor = self.node.style.get("background-color", "transparent")
        else:
            bgcolor = self.node.parent.style.get("background-color", "transparent")
        x2, y2 = self.x + self.width, self.y + self.height
        rect = draw.DrawRect(self.x, self.y, x2, y2, color_to_tuple(bgcolor))
        cmds.append(rect)
        return cmds
