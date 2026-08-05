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
        cmds.append(draw.DrawText(0, 0, self.address_bar if self.focus == "address" else str(self.browser.active_tab.url or "") if self.browser.active_tab else "", (), (0, 0, 1), (1, 1, 1)))
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
                # navigation runs on the tab's main thread, like all tab work
                self.browser.schedule_tab_task(
                    tasks.Task(self.browser.active_tab.load, url.URL(self.address_bar)))
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
        self.measure = tasks.MeasureTime()
        self.draw_lock = threading.Lock()  # draw runs on both threads
        display.detect_sixel()  # before anything else reads stdin
        display.p("\033[?1049h") # Switch to alternate screen buffer
        display.cur((0, 0))
        self.animation_timer = None

    def loop(self):
        display.hide_cursor()
        while True:
            key = display.read_key()
            try:
                self.handle_input(key)
            except SystemExit:
                return
            except Exception:
                # a bad frame must not kill the input thread
                import traceback, js
                js.log_file.write(f"Input error:\n{traceback.format_exc()}\n")
                js.log_file.flush()

    def handle_input(self, key):
            match key:
                case "\004":
                    self.active_tab.dark_mode = not self.active_tab.dark_mode
                    self.active_tab.set_needs_render()  # restyle under the new scheme
                case "\033[A" | "\033[B":
                    # threaded scrolling: just an offset into the last frame's
                    # display list, so it never waits on the main thread
                    self._set_tab_focus()
                    self.active_tab.scroll += 1 if key == "\033[B" else -1
                    self.draw()
                case "\014":
                    #address bar
                    self.focus = self.chrome
                    self.chrome.focus_address_bar()
                case "\033[1;5D":
                    #back
                    self.schedule_tab_task(tasks.Task(self.active_tab.go_back))
                case "q" | "\003":
                    self.quit()
                    raise SystemExit
                case "\011" | "\033[Z":
                    self._set_tab_focus()
                    self.schedule_tab_task(tasks.Task(self.active_tab.handle_key, key))
                case _:
                    if self.focus == self.chrome:
                        self.chrome.handle_key(key)
                        self.draw()
                    elif self.focus:
                        self.schedule_tab_task(tasks.Task(self.active_tab.handle_key, key))

    def quit(self):
        for tab_ in self.tabs:
            tab_.task_runner.set_needs_quit()
        if self.animation_timer:
            self.animation_timer.cancel()
        self.measure.finish()
        display.show_cursor()
        display.p("\033[?1049l") # Switch back to normal screen buffer

    def schedule_tab_task(self, task):
        self.active_tab.task_runner.schedule_task(task)
        self.schedule_animation_frame()  # a frame commits whatever the task changed

    def draw(self):
        with self.draw_lock:
            self.measure.time("draw")
            display.reset()
            self.active_tab.draw(1)
            for cmd in self.chrome.paint():
                cmd.execute(0)
            display.render()
            self.measure.stop("draw")

    def new_tab(self, url):
        new_tab = tab.Tab(self, display.size[1] - 1)
        self.tabs.append(new_tab)
        self.active_tab = new_tab
        self.focus = self.active_tab
        new_tab.task_runner.start_thread()
        new_tab.task_runner.schedule_task(tasks.Task(new_tab.load, url))
        self.schedule_animation_frame()  # paint chrome while the page loads

    def schedule_animation_frame(self):
        def callback():
            self.animation_timer = None
            active_tab = self.active_tab
            task = tasks.Task(active_tab.run_animation_frame)
            active_tab.task_runner.schedule_task(task)
        if not self.animation_timer:
            self.animation_timer = \
                threading.Timer(REFRESH_RATE_SEC, callback)
            self.animation_timer.daemon = True
            self.animation_timer.start()

    def _set_tab_focus(self):
        display.hide_cursor()
        self.chrome.focus = None
        self.focus = self.active_tab
