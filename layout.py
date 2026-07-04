import display
import lexer

import re

class Layout:
    def __init__(self, tokens: list[lexer.Text, lexer.Tag]):
        self.display_list = []
        self.line = []
        self.cursor_x, self.cursor_y = 0, 0
        self.b = False
        self.i = False
        self.WIDTH, self.HEIGHT = display.size[0], display.size[1]
        for tok in tokens:
            self.token(tok)
        self.max_scroll = max(0, self.cursor_y - self.HEIGHT + 1)

    def token(self, tok: lexer.Text | lexer.Tag):
        if isinstance(tok, lexer.Text):
            self.word(tok)
        elif tok.tag == "i":
            self.i = True
        elif tok.tag == "/i":
            self.i = False
        # elif tok.tag == "em":
        #     i = True
        # elif tok.tag == "/em":
        #     i = False
        elif tok.tag == "b":
            self.b = True
        elif tok.tag == "/b":
            self.b = False
        # elif tok.tag == "strong":
        #     b = True
        # elif tok.tag == "/strong":
        #     b = False
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += 1
    
    def word(self, word: lexer.Text):
        toks = word.text.split()
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