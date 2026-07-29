import html

class HTMLNode:
    children: list["HTMLNode"]
    parent: "HTMLNode"
    style: dict[str, str]
    is_focused: bool = False

    def to_html(self) -> str:
        raise NotImplementedError("Subclasses must implement to_html() method.")

class Text(HTMLNode):
    def __init__(self, text, parent):
        self.text: str = text
        self.children = []
        self.parent = parent

    def to_html(self) -> str:
        return html.escape(self.text)
    
    def __repr__(self):
        return repr(self.text)

class Element(HTMLNode):
    def __init__(self, tag, attributes, parent):
        self.tag: str = tag
        self.children = []
        self.attributes: dict[str, str] = attributes
        self.parent = parent

    def to_html(self):
        return "<" + self.tag + "".join(f' {k}="{html.escape(v)}"' for k, v in self.attributes.items()) + ">" + \
               "".join(child.to_html() for child in self.children) + \
               "</" + self.tag + ">"

    def __repr__(self):
        return "<" + self.tag + ">"

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
HEAD_TAGS = [
    "base", "basefont", "bgsound", "noscript",
    "link", "meta", "title", "style", "script",
]
# elements whose contents are text, not markup: everything up to the
# matching close tag is one text node, so "<" inside them isn't a tag
RAWTEXT_TAGS = ["script", "style", "textarea", "title"]

class HTMLParser:
    def __init__(self, body: str):
        self.body: str = body
        self.unfinished: list[HTMLNode] = []
    def parse(self):
        text = ""
        in_tag = False
        rawtext_tag = None
        i = 0
        while i < len(self.body):
            c = self.body[i]
            if rawtext_tag is not None:
                close = "</" + rawtext_tag
                after = self.body[i + len(close):i + len(close) + 1]
                if self.body[i:i + len(close)].casefold() == close \
                   and (after == "" or after == ">" or after == "/" or after.isspace()):
                    if text.strip(): self.add_text(text)
                    text = ""
                    rawtext_tag = None
                    continue
                text += c
                i += 1
                continue
            if c == "<":
                in_tag = True
                if text: self.add_text(text)
                text = ""
            elif c == ">" and in_tag:
                in_tag = False
                self.add_tag(text)
                name = text.strip().split()[0].casefold() if text.strip() else ""
                if name in RAWTEXT_TAGS and not text.rstrip().endswith("/"):
                    rawtext_tag = name
                text = ""
            else:
                text += c
            i += 1
        if not in_tag and text:
            self.add_text(text)
        return self.finish()
    def add_text(self, text: str):
        if text.isspace():
            # whitespace between tags is significant inside the body (it
            # separates inline elements) and inside <pre>; outside the body
            # keeping it would confuse implicit tag insertion
            if not any(isinstance(node, Element) and node.tag in ("body", "pre")
                       for node in self.unfinished):
                return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(html.unescape(text), parent)
        parent.children.append(node)
    def add_tag(self, tag: str):
        self_closing = tag.rstrip().endswith("/") and not tag.startswith("/")
        if self_closing:
            tag = tag.rstrip()[:-1]
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"): return
        self.implicit_tags(tag)
        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS or self_closing:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)
    def get_attributes(self, text: str):
        parts = []
        buf = []
        in_quote = None

        for ch in text:
            if in_quote:
                if ch == in_quote:
                    in_quote = None
                else:
                    buf.append(ch)
            else:
                if ch in ("'", '"'):
                    in_quote = ch
                elif ch.isspace():
                    if buf:
                        parts.append("".join(buf))
                        buf = []
                else:
                    buf.append(ch)

        if buf:
            parts.append("".join(buf))

        # Parse tokens
        if not parts:
            return "", {}

        tag = parts[0].casefold()
        attributes = {}

        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""

        return tag, attributes

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] \
                and tag not in ["head", "body", "/html"]:
                if tag in HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and \
                tag not in ["/head"] + HEAD_TAGS:
                self.add_tag("/head")
            else:
                break
    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)