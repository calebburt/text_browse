import display
import tab
import draw
import url
import tasks

import threading

REFRESH_RATE_SEC = 0.033

class Chrome:
    def __init__(self, browser):
        self.browser: Browser = browser
        self.focus = None
        self.address_bar = ""
    
    def paint(self):
        cmds = []
        cmds.append(draw.DrawRect(0, 0, display.size[0], 1, (0, 0, 1)))
        cmds.append(draw.DrawText(0, 0, self.address_bar if self.focus == "address" else str(self.browser.active_tab.url) if self.browser.active_tab else "", (), (0, 0, 1), (1, 1, 1)))
        return cmds
    
    def focus_address_bar(self):
        self.focus = "address"
        self.address_bar = ""
        display.cur((0, 0))
        display.show_cursor()

    def handle_key(self, key):
        if self.focus == "address":
            if key == "\010" or key == "\177":
                self.address_bar = self.address_bar[:-1]
                display.cur((0, 0))
                display.p("\033[K")
            elif key in ["\012", "\015"]:
                self.browser.active_tab.load(url.URL(self.address_bar))
                self.browser._set_tab_focus()
            else:
                self.address_bar += key
                display.p(key)

class Browser:
    def __init__(self):
        self.tabs = []
        self.active_tab = None
        self.focus = None
        self.chrome = Chrome(self)
        display.p("\033[?1049h") # Switch to alternate screen buffer
        display.cur((0, 0))
        self.animation_timer = None
    
    def loop(self):
        display.hide_cursor()
        while True:
            key = display.read_key()
            if key in ["\033[A", "\033[B", "\011", "\033[Z", "\003"]:
                self._set_tab_focus()
            match key:
                case "\014":
                    #address bar
                    self.focus = self.chrome
                    self.chrome.focus_address_bar()
                case "\033[1;5D":
                    #back
                    self.active_tab.go_back()
                case "q" | "\003":
                    display.show_cursor()
                    display.p("\033[?1049l") # Switch back to normal screen buffer
                    return
                case _:
                    self.focus.handle_key(key) if self.focus else None
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
        self.focus = self.active_tab
        self.draw()

    def schedule_animation_frame(self):
        def callback():
            active_tab = self.active_tab
            task = tasks.Task(active_tab.render)
            active_tab.task_runner.schedule_task(task)
            self.animation_timer = None
        if not self.animation_timer:
            self.animation_timer = \
                threading.Timer(REFRESH_RATE_SEC, callback)
            self.animation_timer.start()

    def _set_tab_focus(self):
        display.hide_cursor()
        self.chrome.focus = None
        self.focus = self.active_tab
