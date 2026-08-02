import threading
import time

class Task:
    def __init__(self, task_code, *args):
        self.task_code = task_code
        self.args = args

    def run(self):
        self.task_code(*self.args)
        self.task_code = None
        self.args = None


class TaskRunner:
    """The tab's main thread: scripts, timers, event handlers, and rendering
    all run here, so single-threaded code (like dukpy) stays single-threaded."""
    def __init__(self, tab):
        self.tab = tab
        self.condition = threading.Condition()
        self.tasks = []
        self.needs_quit = False
        self.main_thread = threading.Thread(
            target=self.run, name="Main thread", daemon=True)

    def start_thread(self):
        self.main_thread.start()

    def schedule_task(self, task):
        with self.condition:
            self.tasks.append(task)
            self.condition.notify_all()

    def clear_pending_tasks(self):
        with self.condition:
            self.tasks.clear()

    def set_needs_quit(self):
        with self.condition:
            self.needs_quit = True
            self.condition.notify_all()

    def run(self):
        while True:
            task = None
            with self.condition:
                if self.needs_quit:
                    return
                if self.tasks:
                    task = self.tasks.pop(0)
                else:
                    self.condition.wait()
            if task:
                try:
                    task.run()
                except Exception:
                    import js, traceback
                    js.log_file.write(f"Task error:\n{traceback.format_exc()}\n")
                    js.log_file.flush()


class MeasureTime:
    """Writes browser.trace in Chrome tracing format: open it in
    chrome://tracing or https://ui.perfetto.dev to profile the browser."""
    def __init__(self):
        self.lock = threading.Lock()
        self.file = open("browser.trace", "w")
        self.file.write('{"traceEvents": [')
        ts = time.time() * 1000000
        self.file.write(
            '{"name": "process_name", "ph": "M", "ts": %d,' % ts +
            ' "pid": 1, "cat": "__metadata",' +
            ' "args": {"name": "Browser"}}')
        self.file.flush()

    def event(self, phase, name):
        ts = time.time() * 1000000
        tid = threading.get_ident()
        with self.lock:
            if self.file.closed: return
            self.file.write(
                ', {"ph": "%s", "cat": "_", "name": "%s",' % (phase, name) +
                ' "ts": %d, "pid": 1, "tid": %d}' % (ts, tid))
            self.file.flush()

    def time(self, name):
        self.event("B", name)

    def stop(self, name):
        self.event("E", name)

    def finish(self):
        with self.lock:
            if self.file.closed: return
            self.file.write(']}')
            self.file.close()
