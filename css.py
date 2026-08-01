import parser

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
    "background-color": "white", # nonstandard
    "white-space": "normal",
    # not inherited in real CSS, but decorations propagate to inline
    # descendants, which inheritance approximates well enough here
    "text-decoration": "none",
}

class Selector:
    priority: int

    def matches(self, node: parser.HTMLNode):
        raise NotImplementedError()

class TagSelector(Selector):
    def __init__(self, tag):
        self.tag: str = tag
        self.priority: int = 1

    def matches(self, node: parser.HTMLNode):
        return isinstance(node, parser.Element) and self.tag == node.tag
    
class ClassSelector(Selector):
    def __init__(self, class_):
        self.class_: str = class_
        self.priority: int = 10
    
    def matches(self, node: parser.HTMLNode):
        return isinstance(node, parser.Element) and "class" in node.attributes and self.class_ in node.attributes["class"].split()

class PseudoclassSelector(Selector):
    def __init__(self, pseudoclass):
        self.pseudoclass: str = pseudoclass
        self.priority: int = 10

    def matches(self, node):
        if self.pseudoclass == "focus":
            return node.is_focused
        else:
            return False
    
class IDSelector(Selector):
    def __init__(self, id):
        self.id: str = id
        self.priority: int = 10
    
    def matches(self, node: parser.HTMLNode):
        return isinstance(node, parser.Element) and "id" in node.attributes and self.id == node.attributes["id"]

class DescendantSelector(Selector):
    def __init__(self, ancestor, descendant):
        self.ancestor: Selector = ancestor
        self.descendant: Selector = descendant
        self.priority: int = self.ancestor.priority + self.descendant.priority

    def matches(self, node: parser.HTMLNode):
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False

class SelectorSequence(Selector):
    def __init__(self, selectors):
        self.selectors: list[Selector] = selectors
        self.priority: int = sum([sel.priority for sel in self.selectors])
    
    def matches(self, node: parser.HTMLNode):
        return all([selector.matches(node) for selector in self.selectors])

class SelectorList(Selector):
    def __init__(self, selectors):
        self.selectors: list[Selector] = selectors
        self.priority: int = sum([sel.priority for sel in self.selectors])
    
    def matches(self, node: parser.HTMLNode):
        return any([selector.matches(node) for selector in self.selectors])

class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def whitespace(self):
        while self.i < len(self.s):
            if self.s[self.i:self.i+2] == "/*":
                self.i += 2
                while self.i < len(self.s) and self.s[self.i:self.i+2] != "*/":
                    self.i += 1
                if self.i < len(self.s):
                    self.i += 2
            elif self.s[self.i].isspace():
                self.i += 1
            else:
                break
    
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i]
    
    def selector_word(self):
        # word() itself can't accept ":", pair() needs it to stop there
        word = self.word()
        while self.i < len(self.s) and self.s[self.i] == ":":
            self.i += 1
            word += ":" + self.word()
        return word

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1

    def value(self):
        start = self.i
        depth = 0
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c in ";}" and depth == 0:
                break
            self.i += 1
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i].strip()

    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.value()
        return prop.casefold(), val

    def simple_selector(self, token):
        selectors = []
        i = 0
        if i < len(token) and token[i] not in ":.#":
            start = i
            while i < len(token) and token[i] not in ":.#":
                i += 1
            selectors.append(TagSelector(token[start:i].casefold()))
        while i < len(token):
            if token[i] not in ":.#":
                raise Exception("Parsing error")
            kind = token[i]
            i += 1
            start = i
            while i < len(token) and token[i] not in ":.#":
                i += 1
            if start == i:
                raise Exception("Parsing error")
            name = token[start:i].casefold()
            if kind == ".":
                selectors.append(ClassSelector(name))
            elif kind == ":":
                selectors.append(PseudoclassSelector(name))
            else:
                selectors.append(IDSelector(name))
        return selectors[0] if len(selectors) == 1 else SelectorSequence(selectors)

    def selector(self):
        selectors = []
        while True:
            self.whitespace()
            out = self.simple_selector(self.selector_word())
            self.whitespace()
            while self.i < len(self.s) and self.s[self.i] not in "{,":
                descendant = self.simple_selector(self.selector_word())
                out = DescendantSelector(out, descendant)
                self.whitespace()
            selectors.append(out)
            self.whitespace()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.literal(",")
                continue
            break
        return selectors[0] if len(selectors) == 1 else SelectorList(selectors)
    
    def body(self):
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules
    
    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None

def style(node: parser.HTMLNode, rules):
    node.style = {}
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value
    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value
    if isinstance(node, parser.Element) and "style" in node.attributes:
        inline_style_text = node.attributes["style"]
        if node.inline_style_text != inline_style_text:
            node.inline_style = CSSParser(inline_style_text).body()
            node.inline_style_text = inline_style_text
        for property, value in node.inline_style.items():
            node.style[property] = value
    for child in node.children:
        style(child, rules)