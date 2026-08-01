import itertools

import display
import parser
import draw

INPUT_WIDTH = 20

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

HIDDEN_ELEMENTS = [
    "script", "style", "meta", "link", "head", "title", "template"
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
    if layout_object.needs_paint():
        display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

def display_type(node):
    """Resolve a node's display for layout: "block", "inline", or "none"."""
    if isinstance(node, parser.Text):
        return "inline"
    if node.tag in HIDDEN_ELEMENTS:
        return "none"
    display = node.style.get("display")
    if display is None:
        return "block" if node.tag in BLOCK_ELEMENTS else "inline"
    display = display.casefold()
    if display == "none":
        return "none"
    if display.startswith("inline") or display == "contents":
        return "inline"
    return "block"  # block, flex, grid, table, list-item, ...

def in_focused_node(node):
    while node:
        if node.is_focused: return True
        node = node.parent
    return False

def decoration_styles(node):
    """Terminal styles for the node's text-decoration."""
    decoration = node.style.get("text-decoration", "none").casefold().split()
    styles = []
    if "underline" in decoration: styles.append("underline")
    if "line-through" in decoration: styles.append("strikethrough")
    return styles

def inline_paint_attrs(child):
    """Background, text color, focus state, and decorations of an inline layout object."""
    node = child.node
    element = node if isinstance(node, parser.Element) else node.parent
    bg = element.style.get("background-color", "transparent")
    color = node.style.get("color", "black")
    return bg, color, in_focused_node(node), decoration_styles(node)

def color_to_tuple(color: str):
    try:
        color = color.casefold()
        if color in COLORS:
            return COLORS[color]
        elif color.startswith("rgb"):
            args = color[color.index("(")+1:color.rindex(")")].replace(",", " ").replace("/", " ").split()
            if len(args) >= 4 and float(args[3]) == 0:
                return None
            return tuple(round(float(a) / 255.0, 3) for a in args[:3])
        elif color[0] == "#":
            color = color.lstrip('#')
            if len(color) in (3, 4):
                color = ''.join(char * 2 for char in color)
            if len(color) == 8 and int(color[6:8], 16) == 0:
                return None
            return tuple(round(int(color[i:i+2], 16) / 255.0, 3) for i in (0, 2, 4))
    except:
        return None

def effective_opacity(node):
    opacity = 1.0
    while node:
        try:
            opacity *= float(node.style.get("opacity", "1"))
        except (TypeError, ValueError):
            pass
        node = node.parent
    return max(0.0, min(1.0, opacity))

def blend_with_background(color, background, opacity):
    if color is None or opacity <= 0:
        return None
    if opacity >= 1:
        return color
    if background is None:
        background = (1, 1, 1)
    return tuple(round(bg + (fg - bg) * opacity, 3)
                 for fg, bg in zip(color, background))

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = display.size[0]
        self.x = 0
        self.y = 0
        child.layout()
        self.display_list = child.display_list
        self.height = child.height

    def needs_paint(self):
        return True

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
            total_width = self.children[-1].x + self.children[-1].width - self.children[0].x

            if text_align == "center":
                offset = (self.width - total_width) // 2
            else:  # "right"
                offset = self.width - total_width

            for child in self.children:
                child.x += offset

    def needs_paint(self):
        return True

    def paint(self):
        # fill the gaps between words that share a background and focus
        # state, so a focused link inverts as one span, not word-by-word;
        # decorations carry across a gap only when both sides have them
        cmds = []
        for prev, child in zip(self.children, self.children[1:]):
            gap = child.x - (prev.x + prev.width)
            bg, color, focused, decorations = inline_paint_attrs(child)
            prev_bg, _, prev_focused, prev_decorations = inline_paint_attrs(prev)
            if gap <= 0 or (bg, focused) != (prev_bg, prev_focused):
                continue
            style = (["inverse"] if focused else []) + [d for d in decorations if d in prev_decorations]
            cmds.append(draw.DrawText(prev.x + prev.width, self.y, " " * gap,
                                      style, color_to_tuple(bg), color_to_tuple(color)))
        return cmds

class TextLayout:
    def __init__(self, node, word, parent, previous, spacing=1):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous
        self.spacing = spacing  # 0 for preformatted text: the word carries its own spaces
        self.x = None
        self.y = None
        self.width = None
        self.height = None
    
    def layout(self):
        self.width = len(self.word)

        if self.previous:
            self.x = self.previous.x + self.previous.width + self.spacing
        else:
            self.x = self.parent.x

        self.height = 1

    def needs_paint(self):
        return True

    def paint(self):
        color = self.node.style["color"]
        bgcolor = self.node.parent.style.get("background-color", "transparent")
        opacity = effective_opacity(self.node)
        if opacity <= 0:
            return []
        background = color_to_tuple(bgcolor)
        font = self.node.style.get("font-weight", "normal") == "bold", self.node.style.get("font-style", "normal") == "italic"
        style = []
        if font[0]:
            style.append("bold")
        if font[1]:
            style.append("italic")
        style += decoration_styles(self.node)
        if in_focused_node(self.node):
            style.append("inverse")
        return [draw.DrawText(self.x, self.y, self.word, style, background,
                              blend_with_background(color_to_tuple(color), background, opacity))]

class InputLayout:
    def __init__(self, node, parent, previous, spacing=1):
        self.node: parser.HTMLNode = node
        self.children = []
        self.parent = parent
        self.previous = previous
        self.spacing = spacing
        self.x, self.y = None, None

    def layout(self):
        self.width = INPUT_WIDTH

        if self.previous:
            self.x = self.previous.x + self.previous.width + self.spacing
        else:
            self.x = self.parent.x

        self.height = 1

    def needs_paint(self):
        return True

    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color", "transparent")
        
        if bgcolor != "transparent":
            rect = draw.DrawRect(self.x, self.y, self.x + self.width, self.y + self.height, color_to_tuple(bgcolor))
            cmds.append(rect)
        
        if self.node.tag == "input" or self.node.tag == "textarea":
            text = self.node.attributes.get("value", "")
            if self.node.attributes.get("type") == "password":
                text = "*" * len(text)
            if not text and not self.node.is_focused:
                text = self.node.attributes.get("placeholder", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and \
               isinstance(self.node.children[0], parser.Text):
                text = self.node.children[0].text
            else:
                text_els = [child for child in self.node.children if isinstance(child, parser.Text)]
                text = " ".join([child.text for child in text_els])
        
        color = self.node.style["color"]
        font = self.node.style.get("font-weight", "normal") == "bold", self.node.style.get("font-style", "normal") == "italic"
        style = []
        if font[0]:
            style.append("bold")
        if font[1]:
            style.append("italic")
        style += decoration_styles(self.node)
        if self.node.is_focused:
            style.append("inverse")
            text = text.ljust(self.width)
        cmds.append(draw.DrawText(self.x, self.y, text, style, color_to_tuple(bgcolor), color_to_tuple(color)))
        return cmds

class BlockLayout:
    def __init__(self, node, parent, previous, inline_nodes=None):
        self.node: parser.HTMLNode = node
        self.parent: BlockLayout | DocumentLayout = parent
        self.previous: BlockLayout = previous
        # anonymous box: lay out just this run of inline siblings
        self.inline_nodes: list[parser.HTMLNode] | None = inline_nodes
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
        if mode == "none":
            self.height = 0
            return
        if mode == "block":
            shown = [c for c in self.node.children if display_type(c) != "none"]
            previous = None
            # a run of consecutive inline-level siblings shares one anonymous box
            for is_block, group in itertools.groupby(shown, lambda c: display_type(c) == "block"):
                run = list(group)
                if is_block:
                    for child in run:
                        previous = BlockLayout(child, self, previous)
                        self.children.append(previous)
                # whitespace between block siblings makes no box of its own
                elif not all(isinstance(n, parser.Text) and n.text.isspace() for n in run):
                    previous = BlockLayout(self.node, self, previous, inline_nodes=run)
                    self.children.append(previous)
        else:
            self.new_line()
            for node in self.inline_nodes or [self.node]:
                self.recurse(node)

        for child in self.children:
            child.layout()

        self.height = sum([child.height for child in self.children])

    def recurse(self, tree):
        if isinstance(tree, parser.Text):
            self.text(tree)
        else:
            if display_type(tree) == "none":
                return
            if tree.tag == "br":
                self.new_line()
            elif tree.tag == "hr":
                self.new_line()
                self.children[-1].children.append(TextLayout(tree, "\u2500" * self.width, self.children[-1], None))
                self.new_line()
            elif tree.tag in ("input", "textarea", "button"):
                if tree.attributes.get("type") == "hidden":
                    return
                self.input(tree)
                return
            for child in tree.children:
                self.recurse(child)
    
    def layout_mode(self):
        if self.inline_nodes is not None:
            return "inline"
        display = display_type(self.node)
        if display in ("none", "inline"):
            return display
        # a block container stacks block-level children vertically;
        # if all its content is inline-level, lay the text out directly
        if any(display_type(child) == "block" for child in self.node.children):
            return "block"
        return "inline"
    
    def text(self, node: parser.Text):
        if node.style.get("white-space", "normal").startswith("pre"):
            self.pre_text(node)
            return
        # a space renders between two words only when the source has
        # whitespace between them; <b>Dave</b>! stays "Dave!"
        words = node.text.split()
        if words and node.text[0].isspace():
            self.pending_space = True
        for i, word in enumerate(words):
            if i: self.pending_space = True
            self.word(node, word)
        if not words or node.text[-1].isspace():
            self.pending_space = True

    def pre_text(self, node: parser.Text):
        lines = node.text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        # a newline right after the <pre> start tag is ignored (HTML spec)
        if lines[0] == "" and getattr(node.parent, "tag", None) == "pre" \
           and node.parent.children[0] is node:
            lines = lines[1:]
        for i, line in enumerate(lines):
            if i > 0:
                self.new_line()
            if not line and i == len(lines) - 1:
                continue  # trailing newline: no extra blank row
            # an empty TextLayout keeps blank lines one row tall
            line = line.expandtabs(8)
            line_layout = self.children[-1]
            previous_word = line_layout.children[-1] if line_layout.children else None
            line_layout.children.append(TextLayout(node, line, line_layout, previous_word, spacing=0))
            self.cursor_x += len(line)

    def word(self, node: parser.HTMLNode, word: str):
        self.place(node, len(word), lambda line, prev, space: TextLayout(node, word, line, prev, spacing=space))

    def input(self, node: parser.HTMLNode):
        self.place(node, INPUT_WIDTH, lambda line, prev, space: InputLayout(node, line, prev, spacing=space))

    def place(self, node, w, make):
        space = 1 if self.pending_space and self.cursor_x > 0 else 0
        if self.cursor_x > 0 and self.cursor_x + space + w > self.width:
            self.new_line()
            space = 0
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        line.children.append(make(line, previous, space))
        self.cursor_x += space + w
        self.pending_space = False

    def new_line(self):
        self.cursor_x = 0
        self.pending_space = False
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def needs_paint(self):
        return isinstance(self.node, parser.Text) or \
            (self.node.tag != "input" and self.node.tag != "button")

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
