import display
import tab
import draw

class Chrome:
    def __init__(self, browser):
        self.browser: Browser = browser
    
    def paint(self):
        cmds = []
        cmds.append(draw.DrawRect(0, 0, display.size[0], 1, (0, 0, 1)))
        cmds.append(draw.DrawText(0, 0, str(self.browser.active_tab.url) if self.browser.active_tab else "", (), (0, 0, 1), (1, 1, 1)))
        return cmds

class Browser:
    def __init__(self):
        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)
        display.p("\033[?1049h") # Switch to alternate screen buffer
        display.cur((0, 0))
    
    def loop(self):
        while True:
            key = display.read_key()
            match key:
                case "\033[A":
                    self.active_tab.scroll -= 1
                case "\033[B":
                    self.active_tab.scroll += 1
                case " ":
                    self.active_tab.scroll += 10
                case "\012" | "\015":
                    self.active_tab.enter()
                case "\011":
                    #forward tab
                    self.active_tab.advance_tab()
                case "\033[Z":
                    #backward tab
                    self.active_tab.advance_tab(backward=True)
                case "q" | "\003":
                    display.show_cursor()
                    display.p("\033[?1049l") # Switch back to normal screen buffer
                    return
            self.active_tab.loop()
            self.draw()
    
    def draw(self):
        display.reset()
        self.active_tab.draw(1)
        for cmd in self.chrome.paint():
            cmd.execute(0)
        display.render()
    
    def new_tab(self, url):
        new_tab = tab.Tab(display.size[1] - 1)
        new_tab.load(url)
        self.tabs.append(new_tab)
        self.active_tab = new_tab
        self.draw()
