import dukpy
import css
import parser
import layout
import tasks

import threading

RUNTIME_JS = open("runtime.js").read()
EVENT_DISPATCH_JS = "new Node(dukpy.handle).dispatchEvent(new Event(dukpy.type))"
SETTIMEOUT_JS = "__runSetTimeout(dukpy.handle)"
XHR_ONLOAD_JS = "__runXHROnload(dukpy.out, dukpy.handle)"

log_file = open("browser.log", "a")

class JSContext:
    def __init__(self, tab):
        self.tab = tab
        self.interp = dukpy.JSInterpreter()

        self.discarded = False

        self.node_to_handle = {}
        self.handle_to_node = {}

        self.interp.export_function("log", lambda arg: log_file.write(str(arg) + "\n"))
        self.interp.export_function("querySelectorAll", self.querySelectorAll)
        self.interp.export_function("getAttribute", self.getAttribute)
        self.interp.export_function("setAttribute", self.setAttribute)
        self.interp.export_function("innerHTML_get", self.innerHTML_get)
        self.interp.export_function("innerHTML_set", self.innerHTML_set)
        self.interp.export_function("setTimeout", self.setTimeout)
        self.interp.export_function("requestAnimationFrame", self.requestAnimationFrame)
        self.interp.export_function("style_set", self.style_set)

        self.interp.evaljs(RUNTIME_JS)

    def run(self, code):
        self.tab.measure.time("script")
        try:
            return self.interp.evaljs(code)
        except Exception as e:
            log_file.write(f"JS Error: {e}\nFor code: {code}\n")
            return None
        finally:
            self.tab.measure.stop("script")


    def get_handle(self, elt):
        if elt not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[elt] = handle
            self.handle_to_node[handle] = elt
        else:
            handle = self.node_to_handle[elt]
        return handle

    def dispatch_event(self, type, elt):
        handle = self.node_to_handle.get(elt, -1)
        do_default = self.interp.evaljs(
            EVENT_DISPATCH_JS, type=type, handle=handle)
        return not do_default


    def querySelectorAll(self, arg1, arg2=None):
        if arg2 is not None:
            selector_text = arg2
            root = self.handle_to_node[arg1]
        else:
            selector_text = arg1
            root = self.tab.nodes
        
        selector = css.CSSParser(selector_text).selector()
        nodes = [node for node
             in layout.tree_to_list(root, [])
             if selector.matches(node)]

        return [self.get_handle(node) for node in nodes]

    def getAttribute(self, handle, attr):
        elt = self.handle_to_node[handle]
        attr = elt.tag if attr == "tag" else elt.attributes.get(attr, None)
        return attr if attr else ""
    def setAttribute(self, handle, attr, value):
        elt = self.handle_to_node[handle]
        elt.attributes[attr] = value
        if attr == "style":
            elt.inline_style_text = None
        self.tab.set_needs_render()

    def innerHTML_set(self, handle, s):
        doc = parser.HTMLParser("<html><body>" + s + "</body></html>").parse()
        new_nodes = doc.children[0].children
        elt = self.handle_to_node[handle]
        elt.children = new_nodes
        for child in elt.children:
            child.parent = elt
        # scripts insert <img> nodes that load() never saw; fetch them in a
        # separate task so the mutation itself returns quickly
        self.tab.task_runner.schedule_task(
            tasks.Task(self.tab.load_images, elt))
        self.tab.set_needs_render()
    def innerHTML_get(self, handle):
        elt = self.handle_to_node[handle]
        return "".join(node.to_html() for node in elt.children)

    def style_set(self, handle, s):
        elt = self.handle_to_node[handle]
        elt.attributes["style"] = s
        elt.inline_style = css.CSSParser(s).body()
        elt.inline_style_text = s
        self.tab.set_needs_render()

    def dispatch_xhr_onload(self, out, handle):
        if self.discarded: return
        do_default = self.interp.evaljs(
            XHR_ONLOAD_JS, out=out, handle=handle)
    def XMLHttpRequest_send(self, method, url, body, isasync, handle):
        full_url = self.tab.url.resolve(url)
        if not self.tab.allowed_request(full_url):
            raise Exception("Cross-origin XHR blocked by CSP")
        if full_url.origin() != self.tab.url.origin():
            raise Exception(
                "Cross-origin XHR request not allowed")

        def run_load():
            headers, response = full_url.request(cross_origin=full_url.host != self.tab.url.host)
            response = response.decode("utf-8", errors="replace")
            task = tasks.Task(self.dispatch_xhr_onload, response, handle)
            self.tab.task_runner.schedule_task(task)
            return response

        if not isasync:
            return run_load()
        else:
            threading.Thread(target=run_load).start()

    def requestAnimationFrame(self):
        if self.discarded: return
        self.tab.browser.schedule_animation_frame()

    def dispatch_settimeout(self, handle):
        if self.discarded: return
        self.interp.evaljs(SETTIMEOUT_JS, handle=handle)
    def setTimeout(self, handle, time):
        def run_callback():
            task = tasks.Task(self.dispatch_settimeout, handle)
            self.tab.task_runner.schedule_task(task)
        threading.Timer(time / 1000.0, run_callback).start()