import display
import parser

import re

class Layout:
    def __init__(self, tree: parser.HTMLNode):
        self.display_list = []
        self.line = []
        self.cursor_x, self.cursor_y = 0, 0
        self.b = False
        self.i = False
        self.WIDTH, self.HEIGHT = display.size[0], display.size[1]
        self.recurse(tree)
        self.max_scroll = max(0, self.cursor_y - self.HEIGHT + 1)
    
    def recurse(self, tree: parser.HTMLNode):
        if isinstance(tree, parser.Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)
    
    def word(self, word: str):
        toks = word.split()
        for word in toks:
            w = len(word)
            if self.cursor_x > 0 and self.cursor_x + w + 1 > self.WIDTH:
                self.flush()
            self.line.append((self.cursor_x, word, (self.b, self.i)))
            self.cursor_x += w + 1
    
    def flush(self):
        self.cursor_y += 1
        self.cursor_x = 0
        for x, word, font in self.line:
            y = self.cursor_y
            self.display_list.append((x, y, word, font))
        self.line = []
    
    def open_tag(self, tag):
        if tag == "i":
            self.i = True
        elif tag == "b":
            self.b = True
        elif tag == "br":
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.i = False
        elif tag == "b":
            self.b = False
        elif tag == "p":
            self.flush()
            self.cursor_y += 1